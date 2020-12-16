from django.db import models
from django.conf import settings
from django.dispatch import receiver

from core.models import LogMixin

from authentication.models import Company

from ballot.constants import POLL_TYPES

from jsonfield import JSONField

# Create your models here.
class LivePoll(LogMixin):
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    is_chosen = models.BooleanField('Is Chosen', default=False)

    class Meta:
        managed = True
        verbose_name = 'Live Poll'
        verbose_name_plural = 'Live Polls'

    def __str__(self):
        return '{}: {}'.format(self.company, self.title)


class LivePollItem(LogMixin):
    poll = models.ForeignKey(LivePoll, related_name='items', on_delete=models.PROTECT)
    order = models.PositiveSmallIntegerField('Sequence Order', default=0)
    text = models.TextField(max_length=1023)
    is_open = models.BooleanField('Is Open', default=False)
    opened_at = models.DateTimeField('Vote Opened At', null=True, blank=True)
    opening_duration_minustes = models.PositiveSmallIntegerField('Vote Opening Duration Minustes', default=5)
    poll_type = models.PositiveSmallIntegerField('Poll Type', choices=POLL_TYPES, default=1)

    class Meta:
        managed = True
        verbose_name = 'Live Poll Item'
        verbose_name_plural = 'Live Poll Items'
        unique_together = ('poll', 'order')
        ordering = ['poll__company', 'order']

    def __str__(self):
        return '{}: {}.{}'.format(self.poll, self.order, self.text)


class LivePollBatch(LogMixin):
    poll = models.ForeignKey(LivePoll, related_name='batchs', on_delete=models.PROTECT)
    batch_no = models.PositiveIntegerField('Batch No.')

    class Meta:
        managed = True
        verbose_name = 'Live Poll Batch'
        verbose_name_plural = 'Live Poll Batches'

    def __str__(self):
        return '{}-{}'.format(self.poll, self.batch_no)


class LivePollItemVote(LogMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_votes', on_delete=models.PROTECT)
    lots = models.SmallIntegerField('Number of Lots', default=0)
    ip_address = models.CharField('IP Address', max_length=15, null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=255, null=True, blank=True)
    poll_item = models.ForeignKey(LivePollItem, related_name='item_votes', on_delete=models.PROTECT)
    poll_batch = models.ForeignKey(LivePollBatch, related_name='batch_votes', on_delete=models.PROTECT, null=True, blank=True)
    vote_option = models.PositiveSmallIntegerField('Vote Option')
    proxy_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='proxy_user_votes', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        managed = True
        verbose_name = 'Live Poll Item Vote'
        verbose_name_plural = 'Live Poll Item Votes'

    def __str__(self):
        return '{}: {} {}'.format(self.poll_item, self.user, self.vote_option)


class LivePollProxy(LogMixin):
    poll_batch = models.ForeignKey(LivePollBatch, related_name='poll_batch_proxys', on_delete=models.PROTECT, null=True, blank=True)
    main_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='main_user_proxys')
    proxy_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='proxy_users_proxys')

    class Meta:
        managed = True
        verbose_name = 'Live Poll Proxy'
        verbose_name_plural = 'Live Poll Proxys'
        unique_together = ('poll_batch', 'main_user')

    def __str__(self):
        return '{}. {}: {}'.format(self.poll_batch, self.main_user, self.proxy_users)


class LivePollResult(LogMixin):
    live_poll = models.OneToOneField(LivePoll, on_delete=models.PROTECT)
    result = JSONField(blank=True, null=True)
    voting_date = models.DateField(verbose_name='Voting Date', auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Live Poll Result'
        verbose_name_plural = 'Live Poll Results'

    def __str__(self):
        return '{}: {}'.format(self.live_poll, self.result)


@receiver(models.signals.post_save, sender=LivePollItem)
def auto_initiate_order_after_save(sender, instance, created, **kwargs):
    """
    Initiate LivePollItem order when object is saved.
    """
    # print('auto_initiate_order_after_save LivePollItem', created)
    if created:
        order_offset = instance.poll.id * 100
        cur_order = instance.poll.items.all().count()
        # print('order_offset cur_order', order_offset, cur_order)
        instance.order = order_offset + cur_order
        instance.save()