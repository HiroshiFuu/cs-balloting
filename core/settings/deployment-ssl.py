# -*- encoding: utf-8 -*-

from .deployment import *  # noqa: F401

# cd /home/it/cs-balloting/
# sudo python3 manage.py runserver_plus --cert-file /home/it/cs-balloting/STAR_cstechsolutions_com_sg/STAR_cstechsolutions_com_sg.crt --key-file /home/it/star_cstechsolutions_com_sg.key

SECRET_KEY = 'jyejjj47s!t1zs%nd@8g4(+qmk(si66ekm1ki!_dhgoe_--iip'

DEBUG = False

RUNSERVERPLUS_SERVER_ADDRESS_PORT = '0.0.0.0:443'

SECURE_SSL_REDIRECT = True

ENVIRON_APPS = [
    'corsheaders',
]

INSTALLED_APPS += ENVIRON_APPS

MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

CORS_ALLOW_ALL_ORIGINS = True