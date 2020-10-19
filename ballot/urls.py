# -*- encoding: utf-8 -*-

from django.urls import path, re_path

from ballot import views

app_name = 'ballot'
urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),

    path('', views.dashboard, name='index'),
    path('home/', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('voting_result_json/<int:survey_id>/', views.voting_result_json, name='voting_result_json'),
    path('surveys/', views.surveys, name='surveys'),
    path('survey/<int:survey_id>/', views.survey, name='survey'),
    path('<int:survey_id>/vote/', views.survey_vote, name='survey_vote'),
    path('survery_vote_done/<int:survey_id>/<int:survey_option_id>/', views.survery_vote_done, name='survery_vote_done'),
    path('live_voting/', views.live_voting, name='live_voting'),
    path('start_next_batch/<int:poll_id>/', views.start_next_batch, name='start_next_batch'),
    path('cur_live_voting/', views.cur_live_voting, name='cur_live_voting'),
    path('open_live_voting/<int:poll_item_id>/', views.open_live_voting, name='open_live_voting'),
    path('close_live_voting/<int:poll_item_id>/', views.close_live_voting, name='close_live_voting'),
    path('live_voting_openning_json/', views.live_voting_openning_json, name='live_voting_openning_json'),
    path('<int:live_poll_id>/live_vote/', views.live_poll_vote, name='live_poll_vote'),
]
