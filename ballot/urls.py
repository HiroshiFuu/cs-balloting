# -*- encoding: utf-8 -*-

from django.urls import path, re_path

from ballot import views

app_name = 'ballot'

urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),
    path('', views.dashboard, name='dashboard'),
    path('home/', views.dashboard, name='home'),
]
