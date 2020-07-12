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


@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='/login/')
def polls(request):
    polls = Poll.objects.all()
    return render(request, 'ui-polls.html', {'polls': polls})


@login_required(login_url='/login/')
def poll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'ballot.html', {'poll': poll})


@login_required(login_url='/login/')
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    print('poll_option', request.POST['poll_option'])
    try:
        poll_option = poll.options.get(pk=request.POST['poll_option'])
        # print(poll_option)
        # print(request.user.weight)
        vote = Voting.objects.create(user=request.user, poll_option=poll_option)
        print(vote)
        poll_result, created = PollResult.objects.get_or_create(poll=poll)
        print(poll_result)
        results = {}
        for vote in Voting.objects.filter(poll_option__poll=poll):
            print(vote)

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
        'PollOptionl': poll_option.text,
        
    }
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


