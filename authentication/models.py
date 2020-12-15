# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator

from core.settings.base import SITE_ID
from core.models import LogMixin

from .constants import USER_TYPES
from .constants import USER_TYPE_USER


class Company(LogMixin):
    name = models.CharField('Name', max_length=63)
    address = models.CharField('Address', max_length=127)
    postal_code = models.PositiveIntegerField('Postal Code')
    valid_date = models.DateField('Valid Date')

    class Meta:
        managed = True
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return '{} {}'.format(self.name, self.valid_date)


class AuthUser(AbstractUser):
    weight = models.PositiveSmallIntegerField(
        'Vote Weightage', null=True, blank=True)
    user_type = models.PositiveSmallIntegerField(
        'User Type', choices=USER_TYPES, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True)
    phone_no = models.CharField(
        'Phone Number', max_length=31, null=True, blank=True)

    class Meta:
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return '{} {} {}'.format(self.username, self.user_type, self.company)

    def lots_details(self):
        "Returns the person's lots details."
        return [lot.block_no + ' ' + lot.unit_no for lot in self.user_lots]


class Lot(LogMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='user_lots', on_delete=models.CASCADE)
    block_no = models.CharField(
        'Block Number', max_length=7, null=True, blank=True)
    unit_no = models.CharField(
        'Unit Number', max_length=15, null=True, blank=True)

    class Meta:
        managed = True
        verbose_name = 'Lot'
        verbose_name_plural = 'Lots'

    def __str__(self):
        return '{}: {} {}'.format(self.user, self.block_no, self.unit_no)


class AuthGroup(Group):
    class Meta:
        proxy = True
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'


@receiver(post_save, sender=AuthUser)
def set_group_when_created_company_user(sender, instance, created, *args, **kwargs):
    if not instance.is_superuser and instance.is_staff:
        company_group = Group.objects.get(name='CompanyUserGroup')
        company_group.user_set.add(instance)


@receiver(post_save, sender=AuthUser)
def send_password_reset_email_when_created(sender, instance, created, *args, **kwargs):
    if created and not instance.is_superuser:
        user = AuthUser._default_manager.get(
            username__iexact=instance.username, is_active=True)
        current_site = Site.objects.get(id=SITE_ID)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            'email': user.username,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'http',
        }
        subject = loader.render_to_string(
            'registration/password_reset_subject.txt', context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(
            'registration/password_reset_email.html', context)
        email_message = EmailMultiAlternatives(
            subject, body, 'admin@abc.com', [user.username])
        email_message.send()
