# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django import template

from .models import Poll, PollOption
from .models import Voting
from .models import PollResult
from authentication.models import User

from django.db.models import Count
from django.db.models import Sum

from collections import defaultdict
from datetime import date


@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='/login/')
def dashboard(request):
    polls = Poll.objects.all()
    polls_details = []
    count_users = len(User.objects.filter(is_staff=False, is_active=True))
    for poll in polls:
        poll_details = {}
        poll_details['id'] = poll.id
        poll_details['title'] = poll.title
        poll_details['created_at'] = poll.created_at
        count_votes = len(Voting.objects.filter(poll_option__poll=poll))
        poll_details['complete_rate'] = count_votes * 1.0 / count_users
        poll_details['complete'] = poll_details['complete_rate'] * 100
        poll_details['end_date'] = 'Unlimited'
        poll_details['days_left'] = 0
        if poll.end_date is not None:
            total = (poll.end_date - poll.created_at.date()).days
            poll_details['end_date'] = poll.end_date
            delta = (poll.end_date - date.today()).days
            poll_details['days_left_ratio'] = (total - delta) * 1.0 / total
            if poll_details['days_left_ratio'] == 0:
                poll_details['days_left_ratio'] = 0.5
            poll_details['days_left'] = delta
        poll_details['latest'] = ''
        latest = Voting.objects.filter(poll_option__poll=poll).order_by('-created_at').first()
        if latest is not None:
            poll_details['latest'] = latest.created_at
        polls_details.append(poll_details)
    # print(polls_details)
    poll_chart = polls.first()
    chart_data = {
        'title': poll_chart.title,
        'data': PollResult.objects.filter(poll=poll_chart).first().result,
    }
    # print(chart_data)
    votings = Voting.objects.all()
    return render(request, 'dashboard.html', {'polls_details': polls_details, 'chart_data': chart_data, 'votings': votings})


@login_required(login_url='/login/')
def polls(request):
    polls = Poll.objects.all()
    return render(request, 'ui-polls.html', {'polls': polls})


@login_required(login_url='/login/')
def poll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    vote = Voting.objects.filter(user=request.user, poll_option__poll=poll).first()
    if vote is not None:
        return HttpResponseRedirect(reverse('ballot:vote_done', args=(poll.id, vote.poll_option.id)))
    return render(request, 'ballot.html', {'poll': poll})


@login_required(login_url='/login/')
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    # print('poll_option', request.POST['poll_option'])
    try:
        poll_option = poll.options.get(pk=request.POST['poll_option'])
        # print(poll_option)
        # print(request.user.weight)
        vote, created = Voting.objects.get_or_create(user=request.user, poll_option=poll_option)
        # print(vote, created)
        if not created:
            print('Something Wrong', 'vote', poll_id)
            return HttpResponseRedirect(reverse('ballot:vote_done', args=(poll.id, poll_option.id)))
        compute_voting_result(poll)
        return HttpResponseRedirect(reverse('ballot:vote_done', args=(poll.id, poll_option.id)))
    except (KeyError, Poll.DoesNotExist, PollOption.DoesNotExist):
        return HttpResponseRedirect(reverse('ballot:poll', args=(poll.id,)))
    return render(request, 'ballot.html', {'poll': poll})


@login_required(login_url='/login/')
def vote_done(request, poll_id, poll_option_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    poll_option = get_object_or_404(PollOption, pk=poll_option_id)
    context = {
        'Poll': poll.title,
        'PollOption': poll_option.text,
    }
    compute_voting_result(poll)
    return JsonResponse(context)


@login_required(login_url='/login/')
def pages(request):
    context = {}
    try:
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('error-404.html')
        return HttpResponse(html_template.render(context, request))
    except:    
        html_template = loader.get_template('error-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url='/login/')
def voting_result_json(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    compute_voting_result(poll)
    chart_data = {
        'title': poll.title,
        'data': PollResult.objects.filter(poll=poll).first().result,
    }
    return JsonResponse(chart_data)


def compute_voting_result(poll):
    poll_result, created = PollResult.objects.get_or_create(poll=poll)
    # print(created, poll_result)
    # votings = Voting.objects.filter(poll_option__poll=poll).values('poll_option__text').annotate(num_votes=Count('poll_option__id'), total_votes=Sum('user__weight'))
    # print(votings)
    results = []
    # for option in poll.options.all():
    #     results[option.text] = 0
    # for voting in votings:
        # results[voting['poll_option__text']] = voting['total_votes']
    # print(results)
    for option in poll.options.all():
        result = {'votes': 0, 'counts': 0}
        result['option'] = option.text
        voting = Voting.objects.filter(poll_option=option).values('poll_option__text').annotate(num_votes=Count('poll_option__id'), total_votes=Sum('user__weight'))
        # print(voting)
        if voting.exists():
            result['votes'] = voting[0]['total_votes']
            result['counts'] = voting[0]['num_votes']
        results.append(result)
    # print(results)
    poll_result.result = results
    poll_result.save()
