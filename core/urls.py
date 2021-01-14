# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('allauth.urls')),
    path('', include('authentication.urls')),
    path('', include('ballot.urls')),
    path('', include('survey.urls')),
    path('', include('live_poll.urls')),
    path('', include('live_poll_multiple.urls')),
    path('', include('api.urls')),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
