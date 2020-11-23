# -*- encoding: utf-8 -*-

from django.urls import path, re_path

from live_poll import views

app_name = 'live_poll'

urlpatterns = [
    path('live_voting/', views.live_voting, name='live_voting'),
    path('start_next_batch/<int:poll_id>/', views.start_next_batch, name='start_next_batch'),
    path('cur_live_voting/', views.cur_live_voting, name='cur_live_voting'),
    path('open_live_voting/<int:poll_item_id>/', views.open_live_voting, name='open_live_voting'),
    path('close_live_voting/<int:poll_item_id>/', views.close_live_voting, name='close_live_voting'),
    path('live_voting_openning_json/', views.live_voting_openning_json, name='live_voting_openning_json'),
    path('<int:live_poll_id>/live_vote/', views.live_poll_vote, name='live_poll_vote'),
]