# -*- encoding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext as _

from jsonfield import JSONField


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


class Survey(LogMixin):
    title = models.CharField(max_length=255)
    end_date = models.DateField(null=True, verbose_name='End Date')
    company_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        managed = True
        verbose_name_plural = 'Surveys'

    def __str__(self):
        return '{}: {} {}'.format(self.company_user.username, self.title, self.end_date)


class SurveyOption(LogMixin):
    text = models.CharField(max_length=255)
    survey = models.ForeignKey(
        Survey, related_name='options', on_delete=models.CASCADE)

    class Meta:
        managed = True
        verbose_name = 'Survey Option'
        verbose_name_plural = 'Survey Options'
        unique_together = ('text', 'survey')

    def __str__(self):
        return '{}: {}'.format(self.survey, self.text)


class SurveyVote(LogMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    survey_option = models.ForeignKey(
        SurveyOption, related_name='votes', on_delete=models.CASCADE)

    class Meta:
        managed = True
        verbose_name = 'Survey Vote'
        verbose_name_plural = 'Survey Votes'

    def __str__(self):
        return '{}: {} {}'.format(self.user, self.survey_option.survey, self.survey_option.text)


class SurveyResult(LogMixin):
    survey = models.OneToOneField(Survey, on_delete=models.CASCADE)
    result = JSONField(blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = 'Survey Result'
        verbose_name_plural = 'Survey Results'

    def __str__(self):
        return '{}: {}'.format(self.survey, self.result)
