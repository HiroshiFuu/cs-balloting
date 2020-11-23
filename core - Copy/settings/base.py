# -*- encoding: utf-8 -*-

import environ
from decouple import config
import os

CORE_DIR = environ.Path(__file__) - 2 # core/settings/base.py - 2 = core/
PROJECT_DIR = CORE_DIR - 1
environ.Env.read_env(PROJECT_DIR('.env'))  # reading .env file

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True)

# load production server from .env
ALLOWED_HOSTS = ['localhost', '127.0.0.1', config('SERVER', default='127.0.0.1')]

# Application definition

DJANGO_APPS = [
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

LOCAL_APPS = [ # Enable the inner app
    'authentication',
    'ballot',
    'live_poll_multiple',
]

THIRD_PARTY_APPS = [
    'django_extensions',
    'import_export',
    'adminsortable2',
    'django_user_agents',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'core.middleware.CurrentUserMiddleware',
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    # 'allauth.account.auth_backends.AuthenticationBackend',
    # custom authentication methods, login by e-mail
    # 'authentication.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(CORE_DIR, 'templates'),
            os.path.join(PROJECT_DIR, 'ballot' 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

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
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'werkzeug': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {}
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'core.password_validation.UpperLowerNumericPasswordValidator',
    }
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = False

DATE_FORMAT = 'b d, Y'

DATETIME_FORMAT = 'Y-m-d H:i:s'

PARENT_DIR = PROJECT_DIR - 1
STATIC_ROOT = str(PARENT_DIR('STATIC_ROOT', 'static'))
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'static'),
    os.path.join(PROJECT_DIR, 'ballot', 'static'),
)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

AUTH_USER_MODEL = 'authentication.AuthUser'

LOGIN_REDIRECT_URL = 'ballot:home'
LOGOUT_REDIRECT_URL = 'ballot:home'
# ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
# ACCOUNT_EMAIL_REQUIRED = True

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(PROJECT_DIR, 'password_reset_emails')

SUIT_CONFIG = {
    'ADMIN_NAME': 'Django Suit',
    'HEADER_DATE_FORMAT': 'l, j. F Y',
    'HEADER_TIME_FORMAT': 'H:i:s',

    # forms
    'SHOW_REQUIRED_ASTERISK': True,  # Default True
    'CONFIRM_UNSAVED_CHANGES': True, # Default True

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    # 'MENU_ICONS': {
    #    'sites': 'icon-leaf',
    #    'auth': 'icon-lock',
    # },
    'MENU_OPEN_FIRST_CHILD': False, # Default True
    # 'MENU_EXCLUDE': ('auth.group', 'auth'),
    'MENU': (
        {'app': 'authentication', 'label': 'Authentication and Authentication', 'icon':'icon-lock', 'models': ('authuser', 'authgroup', 'company')},
        {'app': 'ballot'},
        {'app': 'live_poll_multiple', 'label': 'Live Poll Multiple'},
        'sites',
    ),

    # misc
    # 'LIST_PER_PAGE': 15
}