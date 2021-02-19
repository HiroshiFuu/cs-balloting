"""
WSGI configuration

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import sys
import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env(env_file=os.path.join(os.getcwd(), '.env'))
RUN_ENV = env.str('RUN_ENV', 'local')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.' + RUN_ENV)

from django.core.wsgi import get_wsgi_application

# This allows easy placement of apps within the interior core directory.
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_path)

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
application = get_wsgi_application()

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'configuration.settings.deployment-ssl':
    from whitenoise import WhiteNoise
    application = WhiteNoise(application, root='/home/it/STATIC_ROOT/static')

if os.environ.get('DJANGO_SETTINGS_MODULE') == 'configuration.settings.production':
    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
    application = Sentry(application)
