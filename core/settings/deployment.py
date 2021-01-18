# -*- encoding: utf-8 -*-

from .base import *  # noqa: F401

SECRET_KEY = 'za#q^j+$6frru&3*)b0yl=#9wmue%rf38akqux(fjvl-&zy@_l'

DEBUG = True

ALLOWED_HOSTS = ['118.201.195.130', 'eagm.cstechsolutions.com.sg']

RUNSERVERPLUS_SERVER_ADDRESS_PORT = '0.0.0.0:80'

SECURE_SSL_REDIRECT = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
        'OPTIONS': {
            'sql_mode': 'strict_trans_tables',
        }
    }
}

ENVIRON_APPS = [
    'wkhtmltopdf',
]

INSTALLED_APPS += ENVIRON_APPS

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(lineno)d %(message)s',
            'datefmt' : '%Y/%b/%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/home/it/cs-balloting/debug.log',
            'backupCount': 30,
            'when': 'midnight',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'werkzeug': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}