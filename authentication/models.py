# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    weight = models.PositiveSmallIntegerField('Vote Weighting', null=True, blank=True)