# -*- encoding: utf-8 -*-

from django.urls import path, re_path

from . import views

app_name = 'live_poll_multiple'

urlpatterns = [
    path('live_voting_multiple/', views.live_voting_multiple, name='live_voting_multiple'),
    path('cur_live_voting_multiple/', views.cur_live_voting_multiple, name='cur_live_voting_multiple'),
    path('live_voting_multiple_openning_json/', views.live_voting_multiple_openning_json, name='live_voting_multiple_openning_json'),
    path('open_live_voting_multiple/<int:live_poll_id>/', views.open_live_voting_multiple, name='open_live_voting_multiple'),
    path('close_live_voting_multiple/<int:live_poll_id>/', views.close_live_voting_multiple, name='close_live_voting_multiple'),
    path('<int:live_poll_id>/live_vote_multiple/', views.live_poll_multiple_vote, name='live_poll_multiple_vote'),
]