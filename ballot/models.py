# -*- encoding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext as _

from jsonfield import JSONField

# Create your models here.
class LogMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        editable=False, auto_now_add=True, verbose_name='Created At')
    modified_at = models.DateTimeField(
        editable=False, blank=True, null=True, verbose_name='Modified At')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super().save(*args, **kwargs)


class Poll(LogMixin):
    title = models.CharField(max_length=255)
    end_date = models.DateField(null=True, verbose_name='End Date')

    def __str__(self):
        return '{} {}'.format(self.title, self.end_date)


class PollOption(LogMixin):
    text = models.CharField(max_length=255)
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)

    class Meta:
        managed = True
        verbose_name = 'Poll Option'
        verbose_name_plural = 'Poll Options'
        unique_together = ('text', 'poll')

    def __str__(self):
        return '{}: {}'.format(self.poll, self.text)


class Voting(LogMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    poll_option = models.ForeignKey(PollOption, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {} {}'.format(self.user, self.poll_option.poll, self.poll_option.text)


class PollResult(LogMixin):
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE)
    result = JSONField(blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = 'Poll Result'
        verbose_name_plural = 'Poll Results'

    def __str__(self):
        return '{}: {}'.format(self.poll, self.result)
