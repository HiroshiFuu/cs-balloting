# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from ballot import views

urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),

    path('ballot', views.ballot, name='ballot'),
]
