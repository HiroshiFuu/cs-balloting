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

from .models import LivePollMultiple
from .models import LivePollMultipleItem
from .models import LivePollMultipleItemVote
from .models import LivePollMultipleResult
from .models import LivePollMultipleProxy

from authentication.models import AuthUser
from authentication.constants import USER_TYPE_COMPANY
from authentication.constants import USER_TYPE_USER

from datetime import datetime

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
def live_voting_multiple(request):
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        user_company = request.user.company
        polls = LivePollMultiple.objects.filter(company=user_company)
        polls_details = []
        has_voting_opened = False
        users = AuthUser.objects.filter(user_type=USER_TYPE_USER, company=user_company, is_active=True)
        count_users = users.count()
        for poll in polls:
            poll_details = {}
            poll_details['id'] = poll.id
            poll_details['batch_no'] = poll.batch_no
            poll_details['threshold'] = poll.threshold
            poll_details['is_open'] = poll.is_open
            items = []
            poll_items = poll.multiple_items.all()
            poll_details['miss'] = count_users
            poll_details['miss_addon'] = 0
            for proxy_user in LivePollMultipleProxy.objects.filter(main_user__company=user_company, live_poll=poll):
                poll_details['miss_addon'] += proxy_user.proxy_users.count()
            for user in users:
                vote = LivePollMultipleItemVote.objects.filter(user=user, live_poll_item__live_poll=poll).first()
                if vote is not None:
                    poll_details['miss'] -= 1
                proxy = LivePollMultipleProxy.objects.filter(main_user=user, live_poll=poll).first()
                if proxy is not None:
                    poll_details['miss_addon'] -= 1
            for poll_item in poll_items:
                item = {}
                item['text'] = poll_item.text
                votes = poll_item.multiple_item_votes.all()
                item['votes'] = votes.count()
                item['votes_addon'] = 0
                for vote in votes:
                    proxy = LivePollMultipleProxy.objects.filter(main_user=vote.user, live_poll=poll).first()
                    if proxy is not None:
                        item['votes_addon'] += proxy.proxy_users.all().count()
                items.append(item)
            poll_details['items'] = items
            polls_details.append(poll_details)
            if poll.is_open:
                has_voting_opened = True
        # print('polls_details', polls_details)
        return render(request, 'live_voting_multiple.html', {'polls_details': polls_details, 'has_voting_opened': has_voting_opened})
    else:
        if request.user.is_superuser:
            return HttpResponse('Admin Page U/C')
        else:
            return HttpResponseRedirect(reverse('ballot:dashboard', args=()))


@login_required(login_url='/login/')
def cur_live_voting_multiple(request):
    live_poll = LivePollMultiple.objects.filter(company=request.user.company, is_open=True).first()
    live_poll_items = None
    if live_poll is not None:
        opening_seconds_left = live_poll.opening_duration_minustes * 60 - (datetime.now() - live_poll.opened_at).total_seconds()
        if opening_seconds_left <= 0:
            live_poll.is_open = False
            live_poll.save()
            live_poll = None
        # print('cur_live_voting_multiple')
        if LivePollMultipleItemVote.objects.filter(user=request.user, live_poll_item__live_poll=live_poll):
            live_poll = None
        else:
            for item in live_poll.multiple_items.all():
                # print(item, item.multiple_item_votes.all().count())
                if item.multiple_item_votes.all().count() > live_poll.threshold:
                    live_poll = None
                    break
        if live_poll is not None:
            live_poll_items = live_poll.multiple_items.all()
    return render(request, 'cur_live_voting_multiple.html', {'live_poll': live_poll, 'live_poll_items': live_poll_items})


@login_required(login_url='/login/')
def live_voting_multiple_openning_json(request):
    live_poll = LivePollMultiple.objects.filter(company=request.user.company, is_open=True).first()
    if live_poll:
        opening_seconds_left = int(live_poll.opening_duration_minustes * 60 - (datetime.now() - live_poll.opened_at).total_seconds())
        if opening_seconds_left < 0:
            opening_seconds_left = 0
        if opening_seconds_left == 0 and live_poll.is_open:
            live_poll.is_open = False
            live_poll.save()
        opening_data = {
            'live_poll_id': live_poll.pk,
            'opened_at': live_poll.opened_at,
            'opening_duration_minustes': live_poll.opening_duration_minustes,
            'opening_seconds_left': opening_seconds_left
        }
        return JsonResponse(opening_data)
    else:
        return JsonResponse({'opening_seconds_left': -1})


@login_required(login_url='/login/')
def open_live_voting_multiple(request, live_poll_id):
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        LivePollMultiple.objects.update(is_open=False)
        live_poll = LivePollMultiple.objects.get(pk=live_poll_id)
        live_poll.is_open = True
        live_poll.opened_at = datetime.now()
        # live_poll.opening_duration_minustes = 5
        live_poll.save()
    return HttpResponseRedirect(reverse('live_poll_multiple:live_voting_multiple', args=()))


@login_required(login_url='/login/')
def close_live_voting_multiple(request, live_poll_id):
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        live_poll = LivePollMultiple.objects.get(pk=live_poll_id)
        live_poll.is_open = False
        live_poll.save()
    return HttpResponseRedirect(reverse('live_poll_multiple:live_voting_multiple', args=()))


@login_required(login_url='/login/')
def live_poll_multiple_vote(request, live_poll_id):
    live_poll = get_object_or_404(LivePollMultiple, pk=live_poll_id)
    # print('live_poll_item', request.POST['live_poll_item'])
    try:
        vote = LivePollMultipleItemVote.objects.filter(user=request.user, live_poll_item__live_poll=live_poll).first()
        if vote is None:
            live_poll_item_ids = request.POST.getlist('live_poll_items')
            # print('live_poll_multiple_vote', live_poll_item_ids)
            for live_poll_item_id in live_poll_item_ids:
                live_poll_item_id = int(live_poll_item_id)
                live_poll_item = LivePollMultipleItem.objects.get(id=live_poll_item_id)
                # print(live_poll_item)
                # print(get_client_ip(request), get_client_agent(request))
                LivePollMultipleItemVote.objects.create(user=request.user, live_poll_item=live_poll_item, ip_address=get_client_ip(request), user_agent=get_client_agent(request))
                # compute_live_poll_voting_result(live_poll)
            return HttpResponseRedirect(reverse('ballot:dashboard', args=()))
        else:
            print('Something Wrong', 'live_poll_multiple vote', live_poll_id)
            return HttpResponseRedirect(reverse('ballot:dashboard', args=()))
    except (KeyError, LivePollMultipleItem.DoesNotExist, LivePollMultipleItem.DoesNotExist):
        return HttpResponseRedirect(reverse('ballot:dashboard', args=()))
    return HttpResponseRedirect(reverse('live_poll_multiple:cur_live_voting_multiple', args=()))