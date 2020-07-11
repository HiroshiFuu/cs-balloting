# -*- encoding: utf-8 -*-

from django.db import models

# Create your models here.
class Poll(models.Model):
    title = models.CharField(max_length=255)

class PollOptions(models.Model):
    text = models.CharField(max_length=255)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
