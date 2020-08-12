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

from django.db.models import Count
from django.db.models import Sum

from collections import defaultdict
from datetime import date


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
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        surveys = Survey.objects.all().filter(company_user=request.user)
        surveys_details = []
        count_users = len(AuthUser.objects.filter(user_type=USER_TYPE_USER, company_user=request.user, is_active=True))
        for survey in surveys:
            survey_details = {}
            survey_details['id'] = survey.id
            survey_details['title'] = survey.title
            survey_details['created_at'] = survey.created_at
            count_votes = len(SurveyVote.objects.filter(
                survey_option__survey=survey))
            survey_details['complete_rate'] = count_votes * 1.0 / count_users
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
        chart_data = {}
        if survey_chart is not None:
            chart_data = {
                'title': survey_chart.title,
                'data': SurveyResult.objects.filter(survey=survey_chart).first().result,
            }
        # print(chart_data)
        votings = SurveyVote.objects.all()
        return render(request, 'dashboard.html', {'surveys_details': surveys_details, 'chart_data': chart_data, 'votings': votings})
    else:
        return HttpResponseRedirect(reverse('ballot:surveys', args=()))


@login_required(login_url='/login/')
def surveys(request):
    surveys = Survey.objects.all().filter(company_user=request.user)
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
def vote(request, survey_id):
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
            print('Something Wrong', 'vote', survey_id)
            return HttpResponseRedirect(reverse('ballot:vote_done', args=(survey.id, survey_option.id)))
        compute_voting_result(survey)
        return HttpResponseRedirect(reverse('ballot:vote_done', args=(survey.id, survey_option.id)))
    except (KeyError, Survey.DoesNotExist, SurveyOption.DoesNotExist):
        return HttpResponseRedirect(reverse('ballot:survey', args=(survey.id,)))
    return render(request, 'survey.html', {'survey': survey})


@login_required(login_url='/login/')
def vote_done(request, survey_id, survey_option_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    survey_option = get_object_or_404(SurveyOption, pk=survey_option_id)
    context = {
        'Title': survey.title,
        'Option': survey_option.text,
    }
    compute_voting_result(survey)
    return render(request, 'vote_done.html', context)


@login_required(login_url='/login/')
def voting_result_json(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    compute_voting_result(survey)
    chart_data = {
        'title': survey.title,
        'data': SurveyResult.objects.filter(survey=survey).first().result,
    }
    return JsonResponse(chart_data)


def compute_voting_result(survey):
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
