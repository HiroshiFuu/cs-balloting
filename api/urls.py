# -*- encoding: utf-8 -*-

from django.urls import path

from api import views

app_name = 'api'

urlpatterns = [
    path('cur_live_poll_item/', views.RetriveCurLivePollItem.as_view()),
    path('vote_cur_live_poll/', views.VoteCurLivePollItem.as_view()),
    path('live_poll_status/', views.LivePollStatus.as_view()),
]
