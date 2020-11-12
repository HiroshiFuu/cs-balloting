# Overrides
from .base import *  # noqa: F401

SECRET_KEY = 'za#q^j+$6frru&3*)b0yl=#9wmue%rf38akqux(fjvl-&zy@_l'

DEBUG = True

ALLOWED_HOSTS = ['118.201.195.130', 'eagm.cstechsolutions.com.sg']

RUNSERVERPLUS_SERVER_ADDRESS_PORT = '118.201.195.130:8000'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'local.sqlite3',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
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
            'class': 'logging.FileHandler',
            'filename': '/home/it/cs-balloting/debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO',
        },
        'werkzeug': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}