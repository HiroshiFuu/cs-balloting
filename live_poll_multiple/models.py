from django.db import models
from django.conf import settings
from django.dispatch import receiver

from core.models import LogMixin

from authentication.models import Company

from jsonfield import JSONField

# Create your models here.
class LivePollMultiple(LogMixin):
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    is_open = models.BooleanField('Is Open', default=False)
    opened_at = models.DateTimeField('Vote Opened At', null=True, blank=True)
    opening_duration_minustes = models.PositiveSmallIntegerField('Vote Opening Duration Minustes', default=5)
    batch_no = models.PositiveIntegerField('Batch No.', unique=True)
    threshold = models.PositiveIntegerField('Threshold')

    class Meta:
        managed = True
        verbose_name = 'Live Poll Multiple'
        verbose_name_plural = 'Live Poll Multiples'

    def __str__(self):
        return '{}: {} ({})'.format(self.company, self.batch_no, self.threshold)


class LivePollMultipleItem(LogMixin):
    live_poll = models.ForeignKey(LivePollMultiple, related_name='multiple_items', on_delete=models.PROTECT)
    text = models.CharField(max_length=63)

    class Meta:
        managed = True
        verbose_name = 'Live Poll Multiple Item'
        verbose_name_plural = 'Live Poll Multiple Items'
        unique_together = ('live_poll', 'text')
        ordering = ['live_poll__pk', 'text']

    def __str__(self):
        return '{}: {}'.format(self.live_poll, self.text)


class LivePollMultipleItemVote(LogMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    ip_address = models.CharField('IP Address', max_length=15, null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=255, null=True, blank=True)
    live_poll_item = models.ForeignKey(LivePollMultipleItem, related_name='multiple_item_votes', on_delete=models.PROTECT)

    class Meta:
        managed = True
        verbose_name = 'Live Poll Multiple Item Vote'
        verbose_name_plural = 'Live Poll Multiple Item Votes'

    def __str__(self):
        return '{}: {}'.format(self.live_poll_item, self.user)


class LivePollMultipleProxy(LogMixin):
    live_poll = models.ForeignKey(LivePollMultiple, related_name='multiple_proxy_batches', on_delete=models.PROTECT)
    main_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='multiple_main_user')
    proxy_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='multiple_proxy_users')

    class Meta:
        managed = True
        verbose_name = 'Live Poll Multiple Proxy'
        verbose_name_plural = 'Live Poll Multiple Proxys'
        unique_together = ('live_poll', 'main_user')

    def __str__(self):
        return '{} - {}: {}'.format(self.live_poll, self.main_user, self.proxy_users)


class LivePollMultipleResult(LogMixin):
    live_poll = models.OneToOneField(LivePollMultiple, on_delete=models.PROTECT)
    result = JSONField(blank=True, null=True)
    voting_date = models.DateField(verbose_name='Voting Date', blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = 'Live Poll Multiple Result'
        verbose_name_plural = 'Live Poll Multiple Results'

    def __str__(self):
        return '{}: {}'.format(self.live_poll, self.result)