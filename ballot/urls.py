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
    path('voting_result_json/<int:poll_id>/', views.voting_result_json, name='voting_result_json'),
    path('surveys/', views.surveys, name='surveys'),
    path('survey/<int:survey_id>/', views.survey, name='survey'),
    path('<int:survey_id>/vote/', views.vote, name='vote'),
    path('vote_done/<int:survey_id>/<int:survey_option_id>/', views.vote_done, name='vote_done'),
    path('live_voting/', views.live_voting, name='live_voting'),
    path('open_live_voting/<int:poll_item_id>/', views.open_live_voting, name='open_live_voting'),
    path('close_live_voting/<int:poll_item_id>/', views.close_live_voting, name='close_live_voting'),
    path('live_voting_openning_json/', views.live_voting_openning_json, name='live_voting_openning_json'),
]
