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

from authentication.models import AuthUser
from authentication.constants import USER_TYPE_COMPANY
from authentication.constants import USER_TYPE_USER

from live_poll.models import LivePollItemVote

from .constants import POLL_TYPE_BY_SHARE
from .constants import POLL_TYPE_BY_LOT

from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q

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
def dashboard(request):
    if (request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY) or request.user.is_superuser:
        user_company = request.user.company
        if request.user.is_superuser:
            surveys = Survey.objects.all()
        else:
            surveys = Survey.objects.all().filter(company=user_company)
        surveys_details = []
        count_users = len(AuthUser.objects.filter(user_type=USER_TYPE_USER, company=user_company, is_active=True))
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
        live_poll_votings = []
        for vote in LivePollItemVote.objects.filter(poll_item__poll__company=user_company, poll_item__poll__is_chosen=True).order_by('poll_batch', 'poll_item__order'):
            voting_detail = {}
            voting_detail['id'] = vote.id
            if vote.poll_batch:
                voting_detail['batch_no'] = vote.poll_batch.batch_no
            else:
                voting_detail['batch_no'] = None
            voting_detail['item'] = vote.poll_item.text
            voting_detail['option'] = vote.vote_option
            voting_detail['created_at'] = vote.created_at
            voting_detail['username'] = vote.user.username
            live_poll_votings.append(voting_detail)
            if vote.poll_item.poll_type == POLL_TYPE_BY_LOT:
                proxy = LivePollProxy.objects.filter(main_user=vote.user).first()
                if proxy:
                    for user in proxy.proxy_users.all():
                        voting_detail = {}
                        voting_detail['id'] = vote.id
                        voting_detail['batch_no'] = vote.poll_batch.batch_no
                        voting_detail['item'] = vote.poll_item.text
                        voting_detail['option'] = vote.vote_option
                        voting_detail['created_at'] = vote.created_at
                        voting_detail['username'] = user.username + '(' + vote.user.username + ')'
                        live_poll_votings.append(voting_detail)
        print('live_poll_votings', live_poll_votings)
        return render(request, 'dashboard.html', {'surveys_details': surveys_details, 'survey_chart_data': survey_chart_data, 'survey_votings': survey_votings, 'live_poll_votings': live_poll_votings})
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
