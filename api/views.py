from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from live_poll.models import LivePollItem, LivePollBatch, LivePollItemVote, LivePollProxy, LivePollResult
from .serializers import LivePollItemSerializer, LivePollItemVoteSerializer

from authentication.constants import USER_TYPE_USER
from ballot.constants import POLL_TYPE_BY_SHARE, POLL_TYPE_BY_LOT

from django.db.models import Sum

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


def compute_live_poll_voting_result(live_poll):
    live_poll_result, created = LivePollResult.objects.get_or_create(live_poll=live_poll)
    item_result = {}
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
    live_poll_result.result = item_result
    live_poll_result.save()


class RetriveCurLivePollItem(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
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
        serializer = LivePollItemSerializer(poll_item)
        return Response(serializer.data)


class LivePollStatus(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        poll_item = LivePollItem.objects.filter(poll__company=request.user.company, is_open=True).first()
        if poll_item:
            opening_seconds_left = int(poll_item.opening_duration_minustes * 60 - (datetime.now() - poll_item.opened_at).total_seconds())
            if opening_seconds_left < 0:
                opening_seconds_left = -1
            opening_data = {
                'poll_item_id': poll_item.pk,
                'opened_at': poll_item.opened_at,
                'opening_duration_minustes': poll_item.opening_duration_minustes,
                'opening_seconds_left': opening_seconds_left
            }
            return Response(opening_data)
        else:
            return Response({'opening_seconds_left': -1})


class VoteCurLivePollItem(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LivePollItemVoteSerializer(data=request.data)
        if serializer.is_valid():
            try:
                #{"poll_item":1,"vote_option":2}
                poll_item = LivePollItem.objects.get(pk=serializer.data['poll_item'], is_open=True)
                vote_option = int(serializer.data['vote_option'])
                live_poll = poll_item.poll
                batch = LivePollBatch.objects.filter(poll=live_poll).order_by('-batch_no').first()
                vote = LivePollItemVote.objects.filter(user=request.user, poll_item=poll_item, vote_option=vote_option, poll_batch=batch).first()
                if vote is None and request.user.user_type == USER_TYPE_USER:
                    LivePollItemVote.objects.create(user=request.user, lots=request.user.lots, poll_item=poll_item, poll_batch=batch, vote_option=vote_option, ip_address=get_client_ip(request), user_agent=get_client_agent(request))
                    proxy = LivePollProxy.objects.filter(poll_batch=batch, main_user=request.user).first()
                    if proxy is not None:
                        for proxy_user in proxy.proxy_users.all():
                            LivePollItemVote.objects.create(user=proxy_user, lots=proxy_user.lots, poll_item=poll_item, poll_batch=batch, vote_option=vote_option, ip_address=get_client_ip(request), user_agent=get_client_agent(request), proxy_user=request.user)
                    compute_live_poll_voting_result(live_poll)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    print('Something Really Wrong', 'VoteCurLivePollItem', request.data)
                    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except (KeyError, LivePollItem.DoesNotExist):
                print('Something Wrong', 'VoteCurLivePollItem', request.data)
                Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)