# -*- encoding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.conf import settings

from core.middleware import get_current_user


class LogMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        editable=False, auto_now_add=True, verbose_name='Created At')
    modified_at = models.DateTimeField(
        editable=False, blank=True, null=True, verbose_name='Modified At')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Created By', related_name='%(app_label)s_%(class)s_created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Modified By', related_name='%(app_label)s_%(class)s_modified_by')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
            self.created_by = get_current_user()
        self.modified_at = timezone.now()
        self.modified_by = get_current_user()
        return super().save(*args, **kwargs)