# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

# Create your models here.
class User(AbstractUser):
    weight = models.PositiveSmallIntegerField('Vote Weighting', blank=False)
    email = models.EmailField(_('email address'), blank=False)