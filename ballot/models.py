# -*- encoding: utf-8 -*-

from django.db import models
from django.conf import settings

from core.models import LogMixin

from authentication.models import Company

from .constants import POLL_TYPES

from jsonfield import JSONField


class Survey(LogMixin):
    title = models.CharField(max_length=255)
    end_date = models.DateField(null=True, verbose_name='End Date')
    company = models.ForeignKey(Company, on_delete=models.PROTECT)

    class Meta:
        managed = True
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'

    def __str__(self):
        return '{}: {} {}'.format(self.company, self.title, self.end_date)


class SurveyOption(LogMixin):
    text = models.CharField(max_length=255)
    survey = models.ForeignKey(
        Survey, related_name='options', on_delete=models.PROTECT)

    class Meta:
        managed = True
        verbose_name = 'Survey Option'
        verbose_name_plural = 'Survey Options'
        unique_together = ('text', 'survey')

    def __str__(self):
        return '{}: {}'.format(self.survey, self.text)


class SurveyVote(LogMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    survey_option = models.ForeignKey(
        SurveyOption, related_name='votes', on_delete=models.PROTECT)

    class Meta:
        managed = True
        verbose_name = 'Survey Vote'
        verbose_name_plural = 'Survey Votes'

    def __str__(self):
        return '{}: {} {}'.format(self.user, self.survey_option.survey, self.survey_option.text)


class SurveyResult(LogMixin):
    survey = models.OneToOneField(Survey, on_delete=models.PROTECT)
    result = JSONField(blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = 'Survey Result'
        verbose_name_plural = 'Survey Results'

    def __str__(self):
        return '{}: {}'.format(self.survey, self.result)


class LivePoll(LogMixin):
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    is_chosen = models.BooleanField('Is Chosen', default=False)

    class Meta:
        managed = True
        verbose_name = 'Live Poll'
        verbose_name_plural = 'Live Polls'

    def __str__(self):
        return '{}: {} {}'.format(self.company, self.title, self.is_chosen)


class LivePollItem(LogMixin):
    poll = models.ForeignKey(LivePoll, related_name='items', on_delete=models.PROTECT)
    order = models.PositiveSmallIntegerField('Sequence Order', default=0)
    text = models.CharField(max_length=255)
    is_open = models.BooleanField('Is Open', default=False)
    opened_at = models.DateTimeField('Vote Opened At', null=True, blank=True)
    opening_duration_minustes = models.PositiveSmallIntegerField('Vote Opening Duration Minustes', null=True, blank=True)
    poll_type = models.PositiveSmallIntegerField('Poll Type', choices=POLL_TYPES, default=1)

    class Meta:
        managed = True
        verbose_name = 'Live Poll Item'
        verbose_name_plural = 'Live Poll Items'
        unique_together = ('text', 'poll')
        ordering = ['order']

    def __str__(self):
        return '{}: {}.{}'.format(self.poll, self.order, self.text)


class LivePollBatch(LogMixin):
    poll = models.ForeignKey(LivePoll, related_name='batches', on_delete=models.PROTECT)
    batch_no = models.PositiveIntegerField('Batch No.')

    class Meta:
        managed = True
        verbose_name = 'Live Poll Batch'
        verbose_name_plural = 'Live Poll Batches'

    def __str__(self):
        return '{}. {}'.format(self.poll, self.batch_no)


class LivePollItemVote(LogMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    ip_address = models.CharField('IP Address', max_length=15, null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=255, null=True, blank=True)
    poll_item = models.ForeignKey(LivePollItem, related_name='item_votes', on_delete=models.PROTECT)
    poll_batch = models.ForeignKey(LivePollBatch, related_name='item_batches', on_delete=models.PROTECT, null=True, blank=True)
    vote_option = models.PositiveSmallIntegerField('Vote Option')

    class Meta:
        managed = True
        verbose_name = 'Live Poll Item Vote'
        verbose_name_plural = 'Live Poll Item Votes'

    def __str__(self):
        return '{}: {} {}'.format(self.poll_item, self.user, self.vote_option)


class LivePollProxy(LogMixin):
    poll_batch = models.ForeignKey(LivePollBatch, related_name='proxy_batches', on_delete=models.PROTECT, null=True, blank=True)
    main_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='main_user')
    proxy_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='proxy_users')

    class Meta:
        managed = True
        verbose_name = 'Live Poll Proxy'
        verbose_name_plural = 'Live Poll Proxys'
        unique_together = ('poll_batch', 'main_user')

    def __str__(self):
        return '{}. {}: {}'.format(self.poll_batch, self.main_user, self.proxy_users)


class LivePollResult(LogMixin):
    live_poll = models.OneToOneField(LivePollItem, on_delete=models.PROTECT)
    result = JSONField(blank=True, null=True)
    voting_date = models.DateField(verbose_name='Voting Date', blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = 'Live Poll Result'
        verbose_name_plural = 'Live Poll Results'

    def __str__(self):
        return '{}: {}'.format(self.live_poll, self.result)
