# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django import template
from django.conf import settings

from .models import Survey
from .models import SurveyOption
from .models import SurveyVote
from .models import SurveyResult
from .models import LivePoll
from .models import LivePollItem
from .models import LivePollItemVote
from .models import LivePollResult

from authentication.models import AuthUser
from authentication.constants import USER_TYPE_COMPANY
from authentication.constants import USER_TYPE_USER

from django.db.models import Count
from django.db.models import Sum

from collections import defaultdict
from datetime import date
from datetime import datetime


@staff_member_required
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
def live_voting(request):
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        poll = LivePoll.objects.all().filter(company=request.user.company, is_chosen=True).first()
        poll_details = {}
        if poll:
            count_users = len(AuthUser.objects.filter(user_type=USER_TYPE_USER, company=request.user.company, is_active=True))
            poll_details['title'] = poll.title
            LivePollItems = LivePollItem.objects.filter(poll=poll)
            items = []
            has_voting_opened = False
            for poll_item in LivePollItems:
                item = {}
                item['id'] = poll_item.id
                item['text'] = poll_item.text
                item['is_open'] = poll_item.is_open
                item_result = {}
                smile_count = len(LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=1))
                item_result['smile'] = smile_count
                meh_count = len(LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=2))
                item_result['meh'] = meh_count
                frown_count = len(LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=3))
                item_result['frown'] = frown_count
                item_result['miss'] = count_users - smile_count - meh_count - frown_count
                item['result'] = item_result
                items.append(item)
                if poll_item.is_open:
                    has_voting_opened = True
            poll_details['items'] = items
            # print('poll_details', poll_details)
        return render(request, 'live_voting.html', {'poll_details': poll_details, 'has_voting_opened': has_voting_opened})
    else:
        if request.user.is_superuser:
            return HttpResponse('Admin Page U/C')
        else:
            return HttpResponseRedirect(reverse('ballot:dashboard', args=()))


@login_required(login_url='/login/')
def cur_live_voting(request):
    poll_item = LivePollItem.objects.all().filter(poll__company=request.user.company, is_open=True).first()
    if poll_item is not None:
        opening_seconds_left = poll_item.opening_duration_minustes * 60 - (datetime.now() - poll_item.opened_at).total_seconds()
        if opening_seconds_left <= 0:
            poll_item.is_open = False
            poll_item.save()
            poll_item = None
    return render(request, 'cur_live_voting.html', {'poll_item': poll_item})


@login_required(login_url='/login/')
def open_live_voting(request, poll_item_id):
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        poll_item = LivePollItem.objects.get(pk=poll_item_id)
        poll_item.poll.items.update(is_open=False)
        poll_item.is_open = True
        poll_item.opened_at = datetime.now()
        poll_item.opening_duration_minustes = 5
        poll_item.save()
    return HttpResponseRedirect(reverse('ballot:live_voting', args=()))


@login_required(login_url='/login/')
def close_live_voting(request, poll_item_id):
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        poll_item = LivePollItem.objects.get(pk=poll_item_id)
        poll_item.is_open = False
        poll_item.save()
    return HttpResponseRedirect(reverse('ballot:live_voting', args=()))


@login_required(login_url='/login/')
def live_voting_openning_json(request):
    poll_item = LivePollItem.objects.filter(poll__company=request.user.company, is_open=True).first()
    if poll_item:
        opening_seconds_left = int(poll_item.opening_duration_minustes * 60 - (datetime.now() - poll_item.opened_at).total_seconds())
        if opening_seconds_left < 0:
            opening_seconds_left = 0
        opening_data = {
            'poll_item_id': poll_item.pk,
            'opened_at': poll_item.opened_at,
            'opening_duration_minustes': poll_item.opening_duration_minustes,
            'opening_seconds_left': opening_seconds_left
        }
        return JsonResponse(opening_data)
    else:
        return JsonResponse({'opening_seconds_left': -1})


@login_required(login_url='/login/')
def live_poll_vote(request, live_poll_id):
    live_poll = get_object_or_404(LivePollItem, pk=live_poll_id)
    # print('live_poll_option', request.POST['live_poll_option'])
    try:
        live_poll_option = int(request.POST['live_poll_option'])
        # print(live_poll_option)
        # print(request.user.weight)
        vote = LivePollItemVote.objects.filter(user=request.user, poll_item=live_poll, vote_option=live_poll_option).first()
        if vote is None:
            LivePollItemVote.objects.create(user=request.user, poll_item=live_poll, vote_option=live_poll_option)
            compute_live_poll_voting_result(live_poll)
            return HttpResponseRedirect(reverse('ballot:dashboard', args=()))
        else:
            print('Something Wrong', 'live_poll vote', live_poll_id)
            return HttpResponseRedirect(reverse('ballot:dashboard', args=()))
    except (KeyError, LivePollItem.DoesNotExist, LivePollItem.DoesNotExist):
        return HttpResponseRedirect(reverse('ballot:dashboard', args=()))
    return HttpResponseRedirect(reverse('ballot:cur_live_voting', args=()))


def compute_live_poll_voting_result(live_poll):
    live_poll_result, created = LivePollResult.objects.get_or_create(live_poll=live_poll)
    results = []
    for i in range(3):
        result = {'votes': 0, 'counts': 0}
        result['option'] = i
        voting = LivePollItemVote.objects.filter(vote_option=i).values('poll_item__text').annotate(
            num_votes=Count('poll_item__id'), total_votes=Sum('user__weight'))
        # print(voting)
        if voting.exists():
            result['votes'] = voting[0]['total_votes']
            result['counts'] = voting[0]['num_votes']
        results.append(result)
    print('compute_live_poll_voting_result', results)
    live_poll_result.result = results
    live_poll_result.save()


@login_required(login_url='/login/')
def dashboard(request):
    if (request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY) or request.user.is_superuser:
        if request.user.is_superuser:
            surveys = Survey.objects.all()
        else:
            surveys = Survey.objects.all().filter(company=request.user.company)
        surveys_details = []
        count_users = len(AuthUser.objects.filter(user_type=USER_TYPE_USER, company=request.user.company, is_active=True))
        for survey in surveys:
            survey_details = {}
            survey_details['id'] = survey.id
            survey_details['title'] = survey.title
            survey_details['created_at'] = survey.created_at
            count_votes = len(SurveyVote.objects.filter(
                survey_option__survey=survey))
            if count_users > 0:
                survey_details['complete_rate'] = count_votes * 1.0 / count_users
            else:
                survey_details['complete_rate'] = 0
            survey_details['complete'] = survey_details['complete_rate'] * 100
            survey_details['end_date'] = 'Unlimited'
            survey_details['days_left'] = 0
            if survey.end_date is not None:
                survey_details['end_date'] = survey.end_date
                total = (survey.end_date - survey.created_at.date()).days
                delta = (survey.end_date - date.today()).days
                if total > 0 and delta > 0:
                    survey_details['days_left_ratio'] = (
                        total - delta) * 100.0 / total
                else:
                    survey_details['days_left_ratio'] = 0.5
                if survey_details['days_left_ratio'] < 20:
                    survey_details['days_left_color'] = 'bg-blue'
                elif survey_details['days_left_ratio'] < 70:
                    survey_details['days_left_color'] = 'bg-green'
                elif survey_details['days_left_ratio'] < 85:
                    survey_details['days_left_color'] = 'bg-yellow'
                else:
                    survey_details['days_left_color'] = 'bg-red'
                survey_details['days_left'] = delta
            survey_details['latest'] = ''
            latest = SurveyVote.objects.filter(
                survey_option__survey=survey).order_by('-created_at').first()
            if latest is not None:
                survey_details['latest'] = latest.created_at
            surveys_details.append(survey_details)
        # print(surveys_details)
        survey_chart = surveys.first()
        survey_chart_data = {}
        if survey_chart is not None:
            survery_result = SurveyResult.objects.filter(survey=survey_chart).first()
            if survery_result is not None:
                data = survery_result.result
            else:
                data = {}
            survey_chart_data = {
                'title': survey_chart.title,
                'data': data,
            }
        # print(survey_chart_data)
        survey_votings = SurveyVote.objects.all()
        return render(request, 'dashboard.html', {'surveys_details': surveys_details, 'survey_chart_data': survey_chart_data, 'survey_votings': survey_votings})
    else:
        return HttpResponseRedirect(reverse('ballot:surveys', args=()))


@login_required(login_url='/login/')
def surveys(request):
    if request.user.is_superuser:
        surveys = Survey.objects.all()
    else:
        surveys = Survey.objects.all().filter(company=request.user.company)
    return render(request, 'survey_list.html', {'surveys': surveys})


@login_required(login_url='/login/')
def survey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    vote = SurveyVote.objects.filter(
        user=request.user, survey_option__survey=survey).first()
    if vote is not None:
        return HttpResponseRedirect(reverse('ballot:vote_done', args=(survey.id, vote.survey_option.id)))
    return render(request, 'survey.html', {'survey': survey})


@login_required(login_url='/login/')
def survey_vote(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    # print('survey_option', request.POST['survey_option'])
    try:
        survey_option = survey.options.get(pk=request.POST['survey_option'])
        # print(survey_option)
        # print(request.user.weight)
        vote, created = SurveyVote.objects.get_or_create(
            user=request.user, survey_option=survey_option)
        # print(vote, created)
        if not created:
            print('Something Wrong', 'survey vote', survey_id)
            return HttpResponseRedirect(reverse('ballot:survery_vote_done', args=(survey.id, survey_option.id)))
        compute_survey_voting_result(survey)
        return HttpResponseRedirect(reverse('ballot:survery_vote_done', args=(survey.id, survey_option.id)))
    except (KeyError, Survey.DoesNotExist, SurveyOption.DoesNotExist):
        return HttpResponseRedirect(reverse('ballot:survey', args=(survey.id,)))
    return render(request, 'survey.html', {'survey': survey})


@login_required(login_url='/login/')
def survery_vote_done(request, survey_id, survey_option_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    survey_option = get_object_or_404(SurveyOption, pk=survey_option_id)
    context = {
        'Title': survey.title,
        'Option': survey_option.text,
    }
    compute_survey_voting_result(survey)
    return render(request, 'survery_vote_done.html', context)


@login_required(login_url='/login/')
def voting_result_json(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    compute_survey_voting_result(survey)
    chart_data = {
        'title': survey.title,
        'data': SurveyResult.objects.filter(survey=survey).first().result,
    }
    return JsonResponse(chart_data)


def compute_survey_voting_result(survey):
    survey_result, created = SurveyResult.objects.get_or_create(survey=survey)
    # print(created, survey_result)
    # votings = SurveyVote.objects.filter(survey_option__survey=survey).values('survey_option__text').annotate(num_votes=Count('survey_option__id'), total_votes=Sum('user__weight'))
    # print(votings)
    results = []
    # for option in survey.options.all():
    #     results[option.text] = 0
    # for voting in votings:
    # results[voting['survey_option__text']] = voting['total_votes']
    # print(results)
    for option in survey.options.all():
        result = {'votes': 0, 'counts': 0}
        result['option'] = option.text
        voting = SurveyVote.objects.filter(survey_option=option).values('survey_option__text').annotate(
            num_votes=Count('survey_option__id'), total_votes=Sum('user__weight'))
        # print(voting)
        if voting.exists():
            result['votes'] = voting[0]['total_votes']
            result['counts'] = voting[0]['num_votes']
        results.append(result)
    # print(results)
    survey_result.result = results
    survey_result.save()
