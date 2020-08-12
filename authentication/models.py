# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.contrib.sites.models import Site

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.base_user import AbstractBaseUser

from django.utils.translation import gettext as _
from django.utils import timezone
from django.conf import settings

from core.settings.base import SITE_ID

from .constants import USER_TYPES
from .constants import USER_TYPE_USER

from core.middleware import get_current_user


class LogMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        editable=False, auto_now_add=True, verbose_name='Created At')
    modified_at = models.DateTimeField(
        editable=False, blank=True, null=True, verbose_name='Modified At')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Created By', related_name='user_created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Modified By', related_name='user_modified_by')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
            self.created_by = get_current_user()
        self.modified_at = timezone.now()
        self.modified_by = get_current_user()
        return super().save(*args, **kwargs)


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

    class Meta:
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return '{} {} {}'.format(self.username, self.user_type, self.company)


class AuthGroup(Group):
    class Meta:
        proxy = True
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'


# class CompanyUser(AbstractBaseUser):
#     username_validator = UnicodeUsernameValidator()

#     username = models.CharField(
#         _('username'),
#         max_length=63,
#         unique=False,
#         help_text=_('Required. 63 characters or fewer. Letters, digits and @/./+/-/_ only.'),
#         validators=[username_validator],
#         error_messages={
#             'unique': _("A user with that username already exists."),
#         },
#     )
#     first_name = models.CharField(_('first name'), max_length=63, blank=True)
#     last_name = models.CharField(_('last name'), max_length=63, blank=True)
#     email = models.EmailField(_('email address'))
#     is_staff = models.BooleanField(
#         _('staff status'),
#         default=False,
#         help_text=_('Designates whether the user can log into this admin site.'),
#     )
#     is_active = models.BooleanField(
#         _('active'),
#         default=True,
#         help_text=_(
#             'Designates whether this user should be treated as active. '
#             'Unselect this instead of deleting accounts.'
#         ),
#     )
#     date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
#     weight = models.PositiveSmallIntegerField('Vote Weighting', null=True, blank=False)
#     email = models.EmailField(_('email address'), unique=True, blank=False)
#     company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

#     EMAIL_FIELD = 'email'
#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['email']

#     class Meta:
#         managed = True
#         verbose_name = 'Company User'
#         verbose_name_plural = 'Company Users'


@receiver(post_save, sender=AuthUser)
def set_group_when_created_company_user(sender, instance, created, *args, **kwargs):
    if not instance.is_superuser and instance.is_staff:
        company_group = Group.objects.get(name='CompanyUserGroup')
        company_group.user_set.add(instance)


@receiver(post_save, sender=AuthUser)
def send_password_reset_email_when_created(sender, instance, created, *args, **kwargs):
    if created and not instance.is_superuser:
        user = AuthUser._default_manager.get(
            email__iexact=instance.email, is_active=True)
        current_site = Site.objects.get(id=SITE_ID)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            'email': user.email,
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
            subject, body, 'admin@abc.com', [user.email])
        email_message.send()
