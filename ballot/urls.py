# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from ballot import views

app_name = 'ballot'
urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),

    path('polls/', views.polls, name='polls'),
    path('poll/<int:poll_id>/', views.poll, name='poll'),
    path('<int:poll_id>/vote/', views.vote, name='vote'),
    path('vote_done/<int:poll_id>/<int:poll_option_id>/', views.vote_done, name='vote_done'),
]
