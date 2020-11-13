# Overrides
from .base import *  # noqa: F401

SECRET_KEY = 'za#q^j+$6frru&3*)b0yl=#9wmue%rf38akqux(fjvl-&zy@_l'

DEBUG = True

RUNSERVERPLUS_SERVER_ADDRESS_PORT = '0.0.0.0:8000'

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