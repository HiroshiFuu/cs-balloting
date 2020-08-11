# -*- encoding: utf-8 -*-

from django.urls import path, re_path

from ballot import views

app_name = 'ballot'
urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),

    path('home/', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('voting_result_json/<int:poll_id>/', views.voting_result_json, name='voting_result_json'),
    path('surveys/', views.surveys, name='surveys'),
    path('survey/<int:survey_id>/', views.survey, name='survey'),
    path('<int:survey_id>/vote/', views.vote, name='vote'),
    path('vote_done/<int:survey_id>/<int:survey_option_id>/', views.vote_done, name='vote_done'),
]
