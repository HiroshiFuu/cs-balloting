# -*- encoding: utf-8 -*-

from django.urls import path, re_path

from ballot import views

app_name = 'ballot'

urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),
    path('', views.dashboard, name='dashboard'),
    path('home/', views.dashboard, name='home'),
    path('preview_pdf/<str:app>/', views.preview_pdf, kwargs={'id': None}, name='preview_pdf'),
    path('download_pdf/<str:app>/', views.download_pdf, kwargs={'id': None}, name='download_pdf'),
]
