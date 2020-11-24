# -*- encoding: utf-8 -*-

from django.urls import path, re_path

from survey import views

app_name = 'survey'

urlpatterns = [
    path('voting_result_json/<int:survey_id>/', views.voting_result_json, name='voting_result_json'),
    path('surveys/', views.surveys, name='surveys'),
    path('survey/<int:survey_id>/', views.survey, name='survey'),
    path('<int:survey_id>/vote/', views.survey_vote, name='survey_vote'),
    path('survery_vote_done/<int:survey_id>/<int:survey_option_id>/', views.survery_vote_done, name='survery_vote_done'),
]
