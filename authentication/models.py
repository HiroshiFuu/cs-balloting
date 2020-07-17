# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.utils.translation import gettext as _
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template import loader
from django.core.mail import EmailMultiAlternatives

from core.settings.base import SITE_ID

# Create your models here.
class AdminUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, blank=False)


@receiver(post_save, sender=AdminUser)
def send_password_reset_email_when_created(sender, instance, **kwargs):
    print(instance)
    active_users = get_user_model()._default_manager.filter(
        email__iexact=instance.email, is_active=True)
    for user in (u for u in active_users if u.has_usable_password()):
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
        subject = loader.render_to_string('registration/password_reset_subject.txt', context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string('registration/password_reset_email.html', context)
        email_message = EmailMultiAlternatives(subject, body, 'admin@abc.com', [user.email])
        email_message.send()
        break
