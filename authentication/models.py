# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

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


class CustomUser(AbstractUser):
    weight = models.PositiveSmallIntegerField(
        'Vote Weighting', null=True, blank=True)
    user_type = models.PositiveSmallIntegerField(
        'User Type', choices=USER_TYPES, null=True)
    company_user = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return '{}: {} {}'.format(self.username, self.user_type, self.company_user)


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


@receiver(post_save, sender=CustomUser)
def send_password_reset_email_when_created(sender, instance, created, *args, **kwargs):
    if created:
        user = CustomUser._default_manager.get(
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
