# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .common import *  # noqa

import environ

root = environ.Path(__file__)
env = environ.Env(DEBUG=(bool, False),)
environ.Env.read_env()

DEBUG = env.bool('DJANGO_DEBUG')

SECRET_KEY = env('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# Emails for server notifications.
ADMINS = tuple([tuple(admins.split(':')) for admins in env.list('DJANGO_ADMINS')])

# Emails for project notifications.
# MANAGERS = tuple([tuple(managers.split(':')) for managers in env.list('DJANGO_MANAGERS')])

DATABASES = {
    'default': env.db('DJANGO_DATABASE_URL')
}

EMAIL_URL = env.email_url('DJANGO_EMAIL_URL', default='smtp://user:password@localhost:25')
EMAIL_BACKEND = EMAIL_URL['EMAIL_BACKEND']
EMAIL_HOST = EMAIL_URL.get('EMAIL_HOST', '')
if EMAIL_URL.get('EMAIL_HOST_PASSWORD', '') == 'special':
    EMAIL_HOST_PASSWORD = env('DJANGO_EMAIL_HOST_PASSWORD_SPECIAL')
else:
    EMAIL_HOST_PASSWORD = EMAIL_URL.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = EMAIL_URL.get('EMAIL_HOST_USER', '')
EMAIL_PORT = EMAIL_URL.get('EMAIL_PORT', '')
EMAIL_USE_SSL = 'EMAIL_USE_SSL' in EMAIL_URL
EMAIL_USE_TLS = 'EMAIL_USE_TLS' in EMAIL_URL
EMAIL_FILE_PATH = EMAIL_URL.get('EMAIL_FILE_PATH', '')

DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL')

STATIC_ROOT = env('DJANGO_STATIC_ROOT')
MEDIA_ROOT = env('DJANGO_MEDIA_ROOT')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'mail_admins'],
            'propagate': True
        },
    }
}
