# -*- encoding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.dispatch import receiver

from core.models import LogMixin

from authentication.models import Company

from jsonfield import JSONField

# Create your models here.
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
        Survey, related_name='survey_options', on_delete=models.PROTECT)

    class Meta:
        managed = True
        verbose_name = 'Survey Option'
        verbose_name_plural = 'Survey Options'
        unique_together = ('text', 'survey')

    def __str__(self):
        return '{}: {}'.format(self.survey, self.text)


class SurveyVote(LogMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='survey_user_votes', on_delete=models.PROTECT)
    ip_address = models.CharField('IP Address', max_length=15, null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=255, null=True, blank=True)
    survey_option = models.ForeignKey(
        SurveyOption, related_name='survey_option_votes', on_delete=models.PROTECT)

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
