# -*- encoding: utf-8 -*-

from django.urls import path, re_path

from . import views

app_name = 'live_poll_multiple'

urlpatterns = [
    path('live_voting_multiple/', views.live_voting_multiple, name='live_voting_multiple'),
    path('live_voting_openning_json/', views.live_voting_openning_json, name='live_voting_openning_json'),
]