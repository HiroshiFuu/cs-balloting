# -*- encoding: utf-8 -*-

from .deployment import *  # noqa: F401

# cd /home/it/cs-balloting/
# sudo python3 manage.py runserver_plus --cert-file /home/it/cs-balloting/STAR_cstechsolutions_com_sg/STAR_cstechsolutions_com_sg.crt --key-file /home/it/star_cstechsolutions_com_sg.key

SECRET_KEY = 'jyejjj47s!t1zs%nd@8g4(+qmk(si66ekm1ki!_dhgoe_--iip'

DEBUG = False

RUNSERVERPLUS_SERVER_ADDRESS_PORT = '0.0.0.0:443'

SECURE_SSL_REDIRECT = True

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
            'maxBytes': 10 * 1024 * 1024,
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