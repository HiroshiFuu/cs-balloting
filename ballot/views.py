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
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string

from authentication.models import AuthUser, Company
from authentication.constants import USER_TYPE_COMPANY
from authentication.constants import USER_TYPE_USER

from survey.models import SurveyVote, Survey, SurveyOption
from live_poll.models import LivePollItemVote, LivePollProxy, LivePoll, LivePollItem
from live_poll_multiple.models import LivePollMultipleItemVote, LivePollMultipleProxy, LivePollMultiple, LivePollMultipleItem

from .constants import POLL_TYPE_BY_SHARE
from .constants import POLL_TYPE_BY_LOT

from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q

from datetime import date, datetime
import os

VOTE_OPTIONS_MAPPING = {1: 'For', 2: 'Abstain', 3: 'Against'}


@staff_member_required
@login_required(login_url='/login/')
def populate_pdf_context(request, app=None, id=None):
    user_company = request.user.company
    obj = None
    try:
        if app == 'LPM':
            obj = LivePollMultiple.objects.get(id=int(id))
        if app == 'LP':
            obj = LivePoll.objects.get(id=int(id))
        if app == 'SV':
            obj = Survey.objects.get(id=int(id))
    except Exception as e:
        print(e)
        return None, None, HttpResponse('Something Went Very Very Wrong!')
    if request.user.is_superuser:
        user_company = obj.company
    if user_company is None or obj is None:
        return None, None, HttpResponse('Something Went Very Wrong!')

    context = {}
    filename = None
    if app is not None:
        users = AuthUser.objects.filter(user_type=USER_TYPE_USER, company=user_company, is_active=True)
        total_lots = users.count()
        total_shares = 0
        for user in users:
            total_shares += user.weight
        agm_overview = {'total_lots': total_lots, 'total_shares': total_shares, 'survey': None}

        if app == 'LPM':
            if LivePollMultipleItemVote.objects.filter(live_poll_item__live_poll=obj).first() is None:
                return None, None, HttpResponse('There is no vote yet!')

            context['app'] = '(Live Poll Multiple)'
            agm_overview['batch_no'] = obj.batch_no

            votes = LivePollMultipleItemVote.objects.filter(live_poll_item__live_poll=obj).order_by('created_at')
            first_vote = votes.first()
            last_vote = votes.last()
            agm_overview['meeting_started'] = first_vote.created_at
            agm_overview['meeting_closed'] = last_vote.created_at

            context['agm_overview'] = agm_overview
            context['page_no'] = page_no = 1

            lpm_attendee_pages = {}
            for idx, vote in enumerate(votes, start=0):
                if idx % 2 == 0:
                    page_no += 1
                    lpm_attendee_pages[str(page_no)] = {}
                    lpm_attendees = []
                lpm_attendee = {}
                lpm_attendee['unit_no'] = vote.user.unit_no
                lpm_attendee['name'] = vote.user.username
                for proxy in LivePollMultipleProxy.objects.filter(live_poll=obj):
                    if vote.user in proxy.proxy_users.all():
                        lpm_attendee['name'] += ' (Proxy ' + proxy.main_user.username + ')'
                        break
                lpm_attendee['phone_no'] = vote.user.phone_no
                lpm_attendee['voted_at'] = vote.created_at
                lpm_attendee['ip_address'] = vote.ip_address
                lpm_attendee['user_agent'] = vote.user_agent
                lpm_attendees.append(lpm_attendee)
                lpm_attendee_pages[str(page_no)]['attendees'] = lpm_attendees
            # print('render_pdf', 'lpm_attendee_pages', lpm_attendee_pages)
            context['attendee_pages'] = lpm_attendee_pages

            lpm_record_pages = {}
            record_count = 0
            for idx_item, item in enumerate(LivePollMultipleItem.objects.filter(live_poll=obj), start=0):
                for idx_user, user in enumerate(users, start=0):
                    if record_count % 2 == 0:
                        page_no += 1
                        lpm_record_pages[str(page_no)] = {'text': item.text}
                        lpm_records = []
                    lpm_record = {}
                    lpm_record['voter'] = user.unit_no + ' ' + user.username
                    proxy = user.multiple_proxy_users_proxys.filter(live_poll=obj).first()
                    if proxy is not None:
                        lpm_record['voter'] += ' (Proxy ' + proxy.main_user.username + ')'
                    lpm_record['voted_at'] = None
                    lpm_record['ip_address'] = None
                    vote = item.multiple_item_votes.filter(user=user).first()
                    if vote is not None:
                        lpm_record['voted_at'] = vote.created_at
                        lpm_record['ip_address'] = vote.ip_address
                    record_count += 1
                    lpm_records.append(lpm_record)
                    lpm_record_pages[str(page_no)]['records'] = lpm_records
            # print('render_pdf', 'lpm_record_pages', lpm_record_pages)
            context['record_pages'] = lpm_record_pages

        if app == 'LP':
            if LivePollItemVote.objects.filter(poll_item__poll=obj).first() is None:
                return None, None, HttpResponse('There is no vote yet!')

            context['app'] = '(Live Poll)'
            batch = obj.batchs.order_by('-batch_no').first()
            agm_overview['batch_no'] = batch.batch_no

            votes = batch.batch_votes.order_by('created_at')
            first_vote = votes.first()
            last_vote = votes.last()
            agm_overview['meeting_started'] = first_vote.created_at
            agm_overview['meeting_closed'] = last_vote.created_at

            context['agm_overview'] = agm_overview
            context['page_no'] = page_no = 1

            lp_attendee_pages = {}
            for idx, user in enumerate(users, start=0):
                user_votes = user.user_votes.filter(poll_batch=batch)
                if not user_votes:
                    continue
                if idx % 2 == 0:
                    page_no += 1
                    lp_attendee_pages[str(page_no)] = {}
                    lp_attendees = []
                lp_attendee = {}
                lp_attendee['unit_no'] = user.unit_no
                lp_attendee['name'] = user.username
                for proxy in LivePollProxy.objects.filter(poll_batch=batch):
                    if user in proxy.proxy_users.all():
                        lp_attendee['name'] += ' (Proxy ' + proxy.main_user.username + ')'
                        break
                lp_attendee['phone_no'] = user.phone_no
                vote = user_votes.first()
                lp_attendee['voted_at'] = vote.created_at
                lp_attendee['ip_address'] = vote.ip_address
                lp_attendee['user_agent'] = vote.user_agent
                lp_attendees.append(lp_attendee)
                lp_attendee_pages[str(page_no)]['attendees'] = lp_attendees
            # print('render_pdf', 'lp_attendee_pages', lp_attendee_pages)
            context['attendee_pages'] = lp_attendee_pages

            lp_record_pages = {}
            record_count = 0
            for idx_item, item in enumerate(LivePollItem.objects.filter(poll=obj), start=0):
                for idx_user, user in enumerate(users, start=0):
                    if record_count % 2 == 0:
                        page_no += 1
                        lp_record_pages[str(page_no)] = {'text': item.text}
                        lp_records = []
                    lp_record = {}
                    lp_record['voter'] = user.unit_no + ' ' + user.username
                    proxy = user.proxy_users_proxys.filter(poll_batch=batch).first()
                    if proxy is not None:
                        lp_record['voter'] += ' (Proxy ' + proxy.main_user.username + ')'
                    lp_record['voted_at'] = None
                    lp_record['ip_address'] = None
                    lp_record['vote_option'] = -1
                    vote = item.item_votes.filter(user=user, poll_batch=batch).first()
                    if vote is not None:
                        lp_record['voted_at'] = vote.created_at
                        lp_record['ip_address'] = vote.ip_address
                        lp_record['vote_option'] = VOTE_OPTIONS_MAPPING[vote.vote_option]
                    record_count += 1
                    lp_records.append(lp_record)
                    lp_record_pages[str(page_no)]['records'] = lp_records
            # print('render_pdf', 'lp_record_pages', lp_record_pages)
            context['record_pages'] = lp_record_pages

        if app == 'SV':
            if SurveyVote.objects.filter(survey_option__survey=obj).first() is None:
                return None, None, HttpResponse('There is no vote yet!')

            context['app'] = '(Survey)'
            agm_overview['batch_no'] = obj.id
            agm_overview['survey'] = obj.text

            votes = batch.batch_votes.order_by('created_at')
            first_vote = votes.first()
            last_vote = votes.last()
            agm_overview['meeting_started'] = first_vote.created_at
            agm_overview['meeting_closed'] = last_vote.created_at

            context['agm_overview'] = agm_overview
            context['page_no'] = page_no = 1

            sv_attendee_pages = {}
            for idx, user in enumerate(users, start=0):
                survey_user_votes = user.survey_user_votes
                if not survey_user_votes:
                    continue
                if idx % 2 == 0:
                    page_no += 1
                    sv_attendee_pages[str(page_no)] = {}
                    sv_attendees = []
                sv_attendee = {}
                sv_attendee['unit_no'] = user.unit_no
                sv_attendee['name'] = user.username
                sv_attendee['phone_no'] = user.phone_no
                vote = survey_user_votes.first()
                sv_attendee['voted_at'] = vote.created_at
                sv_attendee['ip_address'] = vote.ip_address
                sv_attendee['user_agent'] = vote.user_agent
                sv_attendees.append(sv_attendee)
                sv_attendee_pages[str(page_no)]['attendees'] = sv_attendees
            # print('render_pdf', 'sv_attendee_pages', sv_attendee_pages)
            context['attendee_pages'] = sv_attendee_pages

            sv_record_pages = {}
            record_count = 0
            for idx_item, option in enumerate(obj.survey_options, start=0):
                for idx_user, user in enumerate(users, start=0):
                    if record_count % 2 == 0:
                        page_no += 1
                        sv_record_pages[str(page_no)] = {'text': option.text}
                        sv_records = []
                    sv_record = {}
                    sv_record['voter'] = user.unit_no + ' ' + user.username
                    sv_record['voted_at'] = None
                    sv_record['ip_address'] = None
                    sv_record['vote_option'] = -1
                    vote = option.survey_option_votes.filter(user=user).first()
                    if vote is not None:
                        sv_record['voted_at'] = vote.created_at
                        sv_record['ip_address'] = vote.ip_address
                    record_count += 1
                    sv_records.append(sv_record)
                    sv_record_pages[str(page_no)]['records'] = sv_records
            # print('render_pdf', 'sv_record_pages', sv_record_pages)
            context['record_pages'] = sv_record_pages

        filename = '{} {} {}.pdf'.format(user_company, context['app'], agm_overview['batch_no'])
        filename = str(filename).replace(' ', '_')

    # print('populate_pdf_context', context, str(filename))
    return context, str(filename), None


@staff_member_required
@login_required(login_url='/login/')
def preview_pdf(request, app=None, id=None):
    html_template = loader.get_template('report_template.html')
    context, filename, error = populate_pdf_context(request, app, id)
    if error:
        return error
    return HttpResponse(html_template.render(context, request))


@staff_member_required
@login_required(login_url='/login/')
def download_pdf(request, app=None, id=None):
    import pdfkit
    context, filename, error = populate_pdf_context(request, app, id)
    if error:
        return error
    html_content = loader.render_to_string('report_template.html', context)
    css_list = [
        os.path.join(settings.STATIC_ROOT, 'report_template_pdfkit.css'),
    ]
    options = {
        'enable-local-file-access': None,
        'page-size': 'A4',
        'orientation': 'Landscape',
        'no-outline': None,
        'margin-top': '0cm',
        'margin-left': '0cm',
        'margin-right': '0cm',
        'margin-bottom': '0cm',
        'dpi': 600,
        'disable-smart-shrinking': None,
    }
    pdf = pdfkit.from_string(
        input=html_content,
        output_path=os.path.join(settings.MEDIA_ROOT, filename),
        css=css_list,
        options=options
    )
    fs = FileSystemStorage(settings.MEDIA_ROOT)
    with fs.open(filename) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response
    return response


# @staff_member_required
# @login_required(login_url='/login/')
# def download_pdf(request, app=None, id=None):
#     from weasyprint import HTML, CSS
#     context, filename = populate_pdf_context(request, app, id)
#     html_string = render_to_string('report_template.html', context)
#     html = HTML(string=html_string)
#     css = CSS(os.path.join(settings.STATIC_ROOT, 'report_template_pdf.css'))
#     target = '/tmp/' + filename
#     print('target', target)
#     html.write_pdf(target=target, stylesheets=[css]);
#     html_template = loader.get_template('report_template.html')
#     fs = FileSystemStorage('/tmp')
#     with fs.open(filename) as pdf:
#         response = HttpResponse(pdf, content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
#         return response
#     return response


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
        # print('live_poll_votings', live_poll_votings)
        return render(request, 'dashboard.html', {'surveys_details': surveys_details, 'survey_chart_data': survey_chart_data, 'survey_votings': survey_votings, 'live_poll_votings': live_poll_votings})
    else:
        return HttpResponseRedirect(reverse('survey:surveys', args=()))
