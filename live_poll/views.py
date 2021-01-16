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

from .models import LivePoll
from .models import LivePollItem
from .models import LivePollItemVote
from .models import LivePollResult
from .models import LivePollProxy
from .models import LivePollBatch

from authentication.models import AuthUser, Company
from authentication.constants import USER_TYPE_COMPANY
from authentication.constants import USER_TYPE_USER

from ballot.constants import POLL_TYPE_BY_SHARE
from ballot.constants import POLL_TYPE_BY_LOT

from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q

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
    return HttpResponseRedirect(reverse('live_poll:live_voting', args=()))


@login_required(login_url='/login/')
def live_voting(request):
    user_company = None
    if request.user.is_superuser:
        try:
            user_company = Company.objects.get(pk=request.POST['company'])
        except (KeyError, Company.DoesNotExist):
            return render(request, 'company_selection.html', {'companys': Company.objects.all(), 'action': '/live_voting/'})
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        user_company = request.user.company
    if user_company is not None:
        poll = LivePoll.objects.filter(company=user_company, is_chosen=True).first()
        poll_details = {}
        has_voting_opened = False
        if poll:
            # compute_live_poll_voting_result(poll)
            users = AuthUser.objects.filter(user_type=USER_TYPE_USER, company=user_company, is_active=True)
            count_users = users.count()
            poll_details['id'] = poll.id
            poll_details['title'] = poll.title
            batch = poll.batchs.order_by('-batch_no').first()
            items = []
            batch_no = None
            if batch is not None:
                batch_no = batch.batch_no
                total_lots = users.aggregate(Count('user_lots'))['user_lots__count'] or 0
                total_shares = users.aggregate(Sum('weight'))['weight__sum'] or 0
                for poll_item in poll.items.all():
                    item = {}
                    item['id'] = poll_item.id
                    item['text'] = poll_item.text
                    item['is_open'] = poll_item.is_open
                    item['type'] = poll_item.poll_type

                    item_result = {}
                    for_votes = LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=1, poll_batch=batch)
                    if poll_item.poll_type == POLL_TYPE_BY_LOT:
                        # for_count = for_votes.count()
                        for_count = for_votes.aggregate(Sum('lots'))['lots__sum'] or 0
                    # for_addon_count = 0
                    # if poll_item.poll_type == POLL_TYPE_BY_LOT:
                    #     for_addon_count = for_votes.filter(proxy_user=None).count()
                    if poll_item.poll_type == POLL_TYPE_BY_SHARE:
                        for_count = for_votes.aggregate(Sum('user__weight'))['user__weight__sum'] or 0
                        # for vote in for_votes:
                        #     for_addon_count += vote.user.weight
                    item_result['for'] = for_count
                    # item_result['for_addon'] = for_addon_count

                    abstain_votes = LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=2, poll_batch=batch)
                    if poll_item.poll_type == POLL_TYPE_BY_LOT:
                        # abstain_count = abstain_votes.count()
                        abstain_count = abstain_votes.aggregate(Sum('lots'))['lots__sum'] or 0
                    # abstain_addon_count = 0
                    # if poll_item.poll_type == POLL_TYPE_BY_LOT:
                    #     abstain_addon_count = abstain_votes.filter(proxy_user=None).count()
                    if poll_item.poll_type == POLL_TYPE_BY_SHARE:
                        abstain_count = abstain_votes.aggregate(Sum('user__weight'))['user__weight__sum'] or 0
                        # for vote in abstain_votes:
                        #     abstain_addon_count += vote.user.weight
                    item_result['abstain'] = abstain_count
                    # item_result['abstain_addon'] = abstain_addon_count

                    against_votes = LivePollItemVote.objects.filter(poll_item=poll_item, vote_option=3, poll_batch=batch)
                    if poll_item.poll_type == POLL_TYPE_BY_LOT:
                        # against_count = against_votes.count()
                        against_count = against_votes.aggregate(Sum('lots'))['lots__sum'] or 0
                    # against_addon_count = 0
                    # if poll_item.poll_type == POLL_TYPE_BY_LOT:
                    #     against_addon_count = against_votes.filter(proxy_user=None).count()
                    if poll_item.poll_type == POLL_TYPE_BY_SHARE:
                        against_count = against_votes.aggregate(Sum('user__weight'))['user__weight__sum'] or 0
                        # for vote in against_votes:
                        #     against_addon_count += vote.user.weight
                    item_result['against'] = against_count
                    # item_result['against_addon'] = against_addon_count
                    item['result'] = item_result
                    
                    # item['miss_addon'] = 0
                    if poll_item.poll_type == POLL_TYPE_BY_LOT:
                        item['total'] = total_lots
                    #     for proxy_user in batch.poll_batch_proxys.all():
                    #         item['miss_addon'] += proxy_user.proxy_users.count()
                    # item['miss_addon'] = item['miss_addon'] - for_addon_count - abstain_addon_count - against_addon_count
                    if poll_item.poll_type == POLL_TYPE_BY_SHARE:
                        item['total'] = total_shares
                    #     for user in AuthUser.objects.filter(user_type=USER_TYPE_USER, company=user_company, is_active=True):
                    #         item['miss_addon'] += user.weight
                    item['miss'] = item['total'] - for_count - abstain_count - against_count
                    # print(item)
                    items.append(item)

                    if poll_item.is_open:
                        has_voting_opened = True
            poll_details['items'] = items
            poll_details['batch_no'] = batch_no
            # print('poll_details', poll_details)
        return render(request, 'live_voting.html', {'poll_details': poll_details, 'has_voting_opened': has_voting_opened})
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
        if LivePollItemVote.objects.filter(user=request.user, poll_item=poll_item, poll_batch=batch):
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
    return HttpResponseRedirect(reverse('live_poll:live_voting', args=()))


@login_required(login_url='/login/')
def close_live_voting(request, poll_item_id):
    if request.user.is_staff and request.user.user_type == USER_TYPE_COMPANY:
        poll_item = LivePollItem.objects.get(pk=poll_item_id)
        poll_item.is_open = False
        poll_item.save()
    return HttpResponseRedirect(reverse('live_poll:live_voting', args=()))


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
    poll_item = get_object_or_404(LivePollItem, pk=live_poll_id)
    # print('live_poll_option', request.POST['live_poll_option'])
    try:
        live_poll_option = int(request.POST['live_poll_option'])
        # print(live_poll_option)
        # print(request.user.weight)
        live_poll = poll_item.poll
        batch = LivePollBatch.objects.filter(poll=live_poll).order_by('-batch_no').first()
        vote = LivePollItemVote.objects.filter(user=request.user, poll_item=poll_item, vote_option=live_poll_option, poll_batch=batch).first()
        if vote is None:
            # print(get_client_ip(request), get_client_agent(request))
            LivePollItemVote.objects.create(user=request.user, lots=request.user.lots, poll_item=poll_item, poll_batch=batch, vote_option=live_poll_option, ip_address=get_client_ip(request), user_agent=get_client_agent(request))
            proxy = LivePollProxy.objects.filter(poll_batch=batch, main_user=request.user).first()
            if proxy is not None:
                for proxy_user in proxy.proxy_users.all():
                    LivePollItemVote.objects.create(user=proxy_user, lots=proxy_user.lots, poll_item=poll_item, poll_batch=batch, vote_option=live_poll_option, ip_address=get_client_ip(request), user_agent=get_client_agent(request), proxy_user=request.user)
            compute_live_poll_voting_result(live_poll)
            return HttpResponseRedirect(reverse('live_poll:cur_live_voting', args=()))
        else:
            print('Something Wrong', 'live_poll_vote', live_poll_id)
            return HttpResponseRedirect(reverse('ballot:dashboard', args=()))
    except (KeyError, LivePollItem.DoesNotExist):
        return HttpResponseRedirect(reverse('ballot:dashboard', args=()))
    return HttpResponseRedirect(reverse('live_poll:cur_live_voting', args=()))


def compute_live_poll_voting_result(live_poll):
    live_poll_result, created = LivePollResult.objects.get_or_create(live_poll=live_poll)
    item_result = {}
    # print(LivePollItemVote.objects.filter(poll_item__poll=live_poll).values('poll_item', 'vote_option').annotate(num_votes=Count('vote_option'), total_votes=Sum('user__weight')))
    for item in live_poll.items.order_by('order'):
        results = []
        for i in [1, 2, 3]:
            result = {'option': i, 'votes': 0}
            votes = item.item_votes.filter(vote_option=i)
            if item.poll_type == POLL_TYPE_BY_SHARE:
                for vote in votes:
                    result['votes'] += vote.user.weight
                result['counts'] = votes.count()
            if item.poll_type == POLL_TYPE_BY_LOT:
                result['votes'] = votes.aggregate(Sum('lots'))['lots__sum'] or 0
                result['proxy_votes'] = votes.exclude(proxy_user=None).aggregate(Sum('lots'))['lots__sum'] or 0
            results.append(result)
        item_result[item.text] = results
    # print('compute_live_poll_voting_result', item_result)
    live_poll_result.result = item_result
    live_poll_result.save()
