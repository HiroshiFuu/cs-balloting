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

from authentication.models import AuthUser
from authentication.constants import USER_TYPE_COMPANY
from authentication.constants import USER_TYPE_USER

from survey.models import Survey, SurveyVote
from live_poll.models import LivePollItemVote, LivePollProxy
from live_poll_multiple.models import LivePollMultipleItemVote, LivePollMultipleProxy, LivePollMultiple, LivePollMultipleItem

from .constants import POLL_TYPE_BY_SHARE
from .constants import POLL_TYPE_BY_LOT

from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q

from datetime import date


@staff_member_required
@login_required(login_url='/login/')
def render_pdf(request, app=None, id=None):
    context = {}
    if app is not None:
        agm_details = {}
        if app == 'LPM':
            context['app'] = '(Live Poll Multiple)'

            lpm = LivePollMultiple.objects.get(id=int(id))
            agm_details['batch_no'] = lpm.batch_no

            user_company = request.user.company
            total_lots = 0
            for proxy_user in LivePollMultipleProxy.objects.filter(main_user__company=user_company, live_poll=lpm):
                total_lots += proxy_user.proxy_users.count()
            total_shares = 0
            users = AuthUser.objects.filter(user_type=USER_TYPE_USER, company=user_company, is_active=True)
            for user in users:
                total_shares += user.weight
            agm_details['total_lots'] = total_lots
            agm_details['total_shares'] = total_shares

            votes = LivePollMultipleItemVote.objects.filter(live_poll_item__live_poll=lpm).order_by('created_at')
            first_vote = votes.first()
            last_vote = votes.last()
            agm_details['meeting_started'] = first_vote.created_at
            agm_details['meeting_closed'] = last_vote.created_at

            context['agm_details'] = agm_details
            page_no = 1

            lpm_attendee_pages = {}
            for idx, vote in enumerate(votes, start=0):
                if idx % 2 == 0:
                    page_no += 1
                    lpm_attendee_pages[str(page_no)] = {}
                    lpm_attendees = []
                lpm_attendee = {}
                lpm_attendee['unit_no'] = vote.user.unit_no
                lpm_attendee['name'] = vote.user.username
                if LivePollMultipleProxy.objects.filter(live_poll=lpm, main_user=vote.user):
                    lpm_attendee['name'] += ' (Proxy)'
                lpm_attendee['phone_no'] = vote.user.phone_no
                lpm_attendee['voted_at'] = vote.created_at
                lpm_attendee['ip_address'] = vote.ip_address
                lpm_attendee['user_agent'] = vote.user_agent
                lpm_attendees.append(lpm_attendee)
                lpm_attendee_pages[str(page_no)]['lpm_attendees'] = lpm_attendees
            # print('render_pdf', 'lpm_attendee_pages', lpm_attendee_pages)
            context['lpm_attendee_pages'] = lpm_attendee_pages

            lpm_record_pages = {}
            record_count = 0
            for idx_item, item in enumerate(LivePollMultipleItem.objects.filter(live_poll=lpm), start=0):
                for idx_user, user in enumerate(AuthUser.objects.filter(user_type=USER_TYPE_USER, company=user_company, is_active=True), start=0):
                    if record_count % 2 == 0:
                        page_no += 1
                        lpm_record_pages[str(page_no)] = {'text': item.text}
                        lpm_records = []
                    lpm_record = {}
                    lpm_record['voter'] = user.unit_no + ' ' + user.username
                    if LivePollMultipleProxy.objects.filter(live_poll=lpm, main_user=user):
                        lpm_record['voter'] += ' (Proxy)'
                    lpm_record['voted_at'] = None
                    lpm_record['ip_address'] = None
                    if item.multiple_item_votes.filter(user=user):
                        lpm_record['voted_at'] = vote.created_at
                        lpm_record['ip_address'] = vote.ip_address
                    record_count += 1
                    lpm_records.append(lpm_record)
                    lpm_record_pages[str(page_no)]['lpm_records'] = lpm_records
            # print('render_pdf', 'lpm_record_pages', lpm_record_pages)
            context['lpm_record_pages'] = lpm_record_pages

    html_template = loader.get_template('report_template.html')
    return HttpResponse(html_template.render(context, request))


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
        return HttpResponseRedirect(reverse('survey:surveys', args=()))
