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
from .models import LivePollProxy
from .models import LivePollBatch

from authentication.models import AuthUser
from authentication.constants import USER_TYPE_COMPANY
from authentication.constants import USER_TYPE_USER
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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_agent(request):
    # Let's assume that the visitor uses an iPhone...
    # request.user_agent.is_mobile # returns True
    # request.user_agent.is_tablet # returns False
    # request.user_agent.is_touch_capable # returns True
    # request.user_agent.is_pc # returns False
    # request.user_agent.is_bot # returns False

    # # Accessing user agent's browser attributes
    # request.user_agent.browser  # returns Browser(family=u'Mobile Safari', version=(5, 1), version_string='5.1')
    # request.user_agent.browser.family  # returns 'Mobile Safari'
    # request.user_agent.browser.version  # returns (5, 1)
    # request.user_agent.browser.version_string   # returns '5.1'

    # # Operating System properties
    # request.user_agent.os  # returns OperatingSystem(family=u'iOS', version=(5, 1), version_string='5.1')
    # request.user_agent.os.family  # returns 'iOS'
    # request.user_agent.os.version  # returns (5, 1)
    # request.user_agent.os.version_string  # returns '5.1'

    # # Device properties
    # request.user_agent.device  # returns Device(family='iPhone')
    # request.user_agent.device.family  # returns 'iPhone'
    return str(request.user_agent.browser) + ' ' + str(request.user_agent.os) + ' ' + str(request.user_agent.device)


@login_required(login_url='/login/')
def start_next_batch(request, poll_id):
    print('start_next_batch', poll_id)
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        poll = LivePoll.objects.get(id=poll_id)
        batch = LivePollBatch.objects.filter(poll=poll).order_by('-batch_no').first()
        if batch is None:
            LivePollBatch.objects.create(poll=poll, batch_no=1)
        else:
            LivePollBatch.objects.create(poll=poll, batch_no=batch.batch_no+1)
    return HttpResponseRedirect(reverse('ballot:live_voting', args=()))


@login_required(login_url='/login/')
def live_voting(request):
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        user_company = request.user.company
        poll = LivePoll.objects.filter(company=user_company, is_chosen=True).first()
        poll_details = {}
        if poll:
            count_users = AuthUser.objects.filter(user_type=USER_TYPE_USER, company=user_company, is_active=True).count()
            poll_details['id'] = poll.id
            poll_details['title'] = poll.title
            batch = LivePollBatch.objects.filter(poll=poll).order_by('-batch_no').first()
            items = []
            has_voting_opened = False
            batch_no = None
            if batch is not None:
                batch_no = batch.batch_no
                poll_items = LivePollItem.objects.filter(poll=poll)
                for poll_item in poll_items:
                    item = {}
                    item['id'] = poll_item.id
                    item['text'] = poll_item.text
                    item['is_open'] = poll_item.is_open
                    item['type'] = poll_item.poll_type
                    item_result = {}

                    # for_count = len(LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=1, poll_batch=batch))
                    for_count = 0
                    for_addon_count = 0
                    for vote in LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=1, poll_batch=batch):
                        for_count = for_count + 1
                        if poll_item.poll_type == POLL_TYPE_BY_SHARE:
                            for_addon_count = for_addon_count + vote.user.weight
                        if poll_item.poll_type == POLL_TYPE_BY_LOT:
                            for_addon_count = for_addon_count + LivePollProxy.objects.filter(main_user=vote.user, poll_batch=batch).count()
                    item_result['for'] = for_count
                    item_result['for_addon'] = for_addon_count
                    # abstain_count = len(LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=2, poll_batch=batch))
                    abstain_count = 0
                    abstain_addon_count = 0
                    for vote in LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=2, poll_batch=batch):
                        abstain_count = abstain_count + 1
                        if poll_item.poll_type == POLL_TYPE_BY_SHARE:
                            abstain_addon_count = abstain_addon_count + vote.user.weight
                        if poll_item.poll_type == POLL_TYPE_BY_LOT:
                            abstain_addon_count = abstain_addon_count + LivePollProxy.objects.filter(main_user=vote.user, poll_batch=batch).count()
                    item_result['abstain'] = abstain_count
                    item_result['abstain_addon'] = abstain_addon_count
                    # against_count = len(LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=3, poll_batch=batch))
                    against_count = 0
                    against_addon_count = 0
                    for vote in LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=3, poll_batch=batch):
                        against_count = against_count + 1
                        if poll_item.poll_type == POLL_TYPE_BY_SHARE:
                            against_addon_count = against_addon_count + vote.user.weight
                        if poll_item.poll_type == POLL_TYPE_BY_LOT:
                            against_addon_count = against_addon_count + LivePollProxy.objects.filter(main_user=vote.user, poll_batch=batch).count()
                    item_result['against'] = against_count
                    item_result['against_addon'] = against_addon_count

                    item_result['miss'] = count_users - for_count - abstain_count - against_count
                    item['result'] = item_result
                    item['addon'] = 0
                    if poll_item.poll_type == POLL_TYPE_BY_SHARE:
                        for user in AuthUser.objects.filter(user_type=USER_TYPE_USER, company=user_company, is_active=True):
                            item['addon'] = item['addon'] + user.weight
                    if poll_item.poll_type == POLL_TYPE_BY_LOT:
                        for proxy_user in LivePollProxy.objects.filter(main_user__company=user_company, poll_batch=batch):
                            item['addon'] += proxy_user.proxy_users.count()
                    items.append(item)
                    if poll_item.is_open:
                        has_voting_opened = True
            poll_details['items'] = items
            poll_details['batch_no'] = batch_no
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
        batch = LivePollBatch.objects.filter(poll=poll_item.poll).order_by('-batch_no').first()
        if batch is not None:
            opening_seconds_left = poll_item.opening_duration_minustes * 60 - (datetime.now() - poll_item.opened_at).total_seconds()
            if opening_seconds_left <= 0:
                poll_item.is_open = False
                poll_item.save()
                poll_item = None
        if LivePollItemVote.objects.filter(poll_item=poll_item, poll_batch=batch):
            poll_item = None
    return render(request, 'cur_live_voting.html', {'poll_item': poll_item})


@login_required(login_url='/login/')
def open_live_voting(request, poll_item_id):
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        poll_item = LivePollItem.objects.get(pk=poll_item_id)
        poll_item.poll.items.update(is_open=False)
        poll_item.is_open = True
        poll_item.opened_at = datetime.now()
        # poll_item.opening_duration_minustes = 5
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
        if opening_seconds_left == 0 and poll_item.is_open:
            poll_item.is_open = False
            poll_item.save()
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
            # print(get_client_ip(request), get_client_agent(request))
            batch = LivePollBatch.objects.filter(poll=live_poll.poll).order_by('-batch_no').first()
            LivePollItemVote.objects.create(user=request.user, poll_item=live_poll, vote_option=live_poll_option, ip_address=get_client_ip(request), user_agent=get_client_agent(request), poll_batch=batch)
            # compute_live_poll_voting_result(live_poll)
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
