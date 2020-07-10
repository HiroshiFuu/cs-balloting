# -*- encoding: utf-8 -*-

from .base import *
import os

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'db.sqlite3'),
    }
}

RUNSERVERPLUS_SERVER_ADDRESS_PORT = '127.0.0.1:8000'