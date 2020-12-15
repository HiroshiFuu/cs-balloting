# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from .models import Survey
from .models import SurveyOption
from .models import SurveyVote
from .models import SurveyResult

from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q

# Create your views here.


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_agent(request):
    return str(request.user_agent.browser) + ' ' + str(request.user_agent.os) + ' ' + str(request.user_agent.device)


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
        return HttpResponseRedirect(reverse('survey:survery_vote_done', args=(survey.id, vote.survey_option.id)))
    return render(request, 'survey.html', {'survey': survey})


@login_required(login_url='/login/')
def survey_vote(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    # print('survey_option', request.POST['survey_option'])
    try:
        survey_option = survey.survey_options.get(
            pk=request.POST['survey_option'])
        # print(survey_option)
        # print(request.user.weight)
        vote, created = SurveyVote.objects.get_or_create(
            user=request.user, survey_option=survey_option, ip_address=get_client_ip(request), user_agent=get_client_agent(request))
        # print(vote, created)
        if not created:
            print('Something Wrong', 'survey vote', survey_id)
            return HttpResponseRedirect(reverse('survey:survery_vote_done', args=(survey.id, survey_option.id)))
        compute_survey_voting_result(survey)
        return HttpResponseRedirect(reverse('survey:survery_vote_done', args=(survey.id, survey_option.id)))
    except (KeyError, Survey.DoesNotExist, SurveyOption.DoesNotExist):
        return HttpResponseRedirect(reverse('survey:survey', args=(survey.id,)))
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
    for option in survey.survey_options.all():
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
