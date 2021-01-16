from rest_framework import serializers

from live_poll.models import LivePollItem, LivePollItemVote


class LivePollItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LivePollItem
        fields = ['id', 'text']


class LivePollItemVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LivePollItemVote
        fields = ['poll_item', 'vote_option']