# -*- coding: utf-8 -*-
"""
Django settings for citifleet project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import os

import environ
import raven
from easy_thumbnails.conf import Settings as thumbnail_settings


ROOT_DIR = environ.Path(__file__) - 2  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path('citifleet')

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, '-z$4z#z7v5g^zx-79xu#qlh-m3m@pb!m_qcylfs%55yytu&5xs'),
    DJANGO_ADMINS=(list, []),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_STATIC_ROOT=(str, str(APPS_DIR('staticfiles'))),
    DJANGO_MEDIA_ROOT=(str, str(APPS_DIR('media'))),
    DJANGO_DATABASE_URL=(str, 'postgis:///cityfleet'),
    DJANGO_EMAIL_URL=(environ.Env.email_url_config, 'consolemail://user@:password@localhost:25'),
    DJANGO_DEFAULT_FROM_EMAIL=(str, 'admin@example.com'),
    DJANGO_EMAIL_BACKEND=(str, 'django.core.mail.backends.smtp.EmailBackend'),
    SERVER_EMAIL=(str, 'root@localhost.com'),
    CELERY_BROKER_URL=(str, 'redis://localhost:6379/0'),
    DJANGO_CELERY_BACKEND=(str, 'redis://localhost:6379/0'),
    APP_TOKEN=(str, ''),  # Socrata token
    CONSUMER_KEY=(str, ''),  # twitter consumer key
    CONSUMER_SECRET=(str, ''),  # twitter consumer secret
    CLIENT_SECRET=(str, ''),  # instagram client secret
    GCM_API_KEY=(str, ''),
    APNS_CERTIFICATE_PATH=(str, ''),
    REDIS_URL=(str, 'redis://localhost:6379'),

    DJANGO_USE_DEBUG_TOOLBAR=(bool, False),
    DJANGO_CELERY_ALWAYS_EAGER=(bool, False),
)
environ.Env.read_env()

DEBUG = env.bool("DJANGO_DEBUG")

SECRET_KEY = env('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

ADMINS = tuple([tuple(admins.split(':')) for admins in env.list('DJANGO_ADMINS')])

MANAGERS = ADMINS

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATABASES = {
    'default': env.db('DJANGO_DATABASE_URL')
}

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.gis',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'easy_thumbnails',
    'image_cropping',
    'push_notifications',
    'channels',
    'constance',
    'constance.backends.database',
    'django_extensions',
)

LOCAL_APPS = (
    'citifleet.reports.apps.ReportsConfig',
    'citifleet.legalaid',
    'citifleet.documents.apps.DocumentsConfig',
    'citifleet.benefits',
    'citifleet.notifications.apps.NotificationsConfig',
    'citifleet.marketplace.apps.MarketplaceConfig',
    'citifleet.chat.apps.ChatConfig',
    'citifleet.users.apps.UsersConfig',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)


# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_URL = env.email_url('DJANGO_EMAIL_URL')
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

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


STATIC_URL = '/static/'
STATIC_ROOT = env('DJANGO_STATIC_ROOT')

MEDIA_URL = '/media/'
MEDIA_ROOT = env('DJANGO_MEDIA_ROOT')

STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:redirect'
ADMIN_URL = r'^admin/'

# celery settigs
BROKER_URL = env('CELERY_BROKER_URL')
CELERY_BACKEND = env('DJANGO_CELERY_BACKEND')
CELERY_ALWAYS_EAGER = env.bool('DJANGO_CELERY_ALWAYS_EAGER')

# Socrata config
TLC_URL = 'data.cityofnewyork.us'
APP_TOKEN = env('APP_TOKEN', default=None)
TLC_FOR_HIRE_DRIVERS = 'p8xb-39i5'
TLC_MEDALLION = 'pm46-7vyh'

# DRF config
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S',
    'PAGE_SIZE': 20,
    'DEFAULT_PAGINATION_CLASS': None
}

VISIBLE_REPORTS_RADIUS = 1000  # meters
AUTOCLOSE_INTERVAL = 60

# Twitter keys
TWITTER_CONSUMER_KEY = env('CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = env('CONSUMER_SECRET')

# Instagram keys
INSTAGRAM_CLIENT_SECRET = env('CLIENT_SECRET')

# Thumbnail config
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS

# Push notifications config
PUSH_NOTIFICATIONS_SETTINGS = {
        "GCM_API_KEY": env('GCM_API_KEY'),
        "APNS_CERTIFICATE": env('APNS_CERTIFICATE_PATH'),
}

# Channels Layer config
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env('REDIS_URL')],
        },
        "ROUTING": "citifleet.chat.routing.channel_routing",
    },
}

# Constance config
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'SODA_CHECK_ENABLED': (True, 'Hack license check via SODA API enabled'),
    'TLC_PUSH_NOTIFICATION_RADIUS': (0.5, 'Radius in miles within which we should send notification about nearby TLC reports'),  # noqa
}

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

if os.environ.get('SENTRY_DSN'):
    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)
    RAVEN_CONFIG = {
        'dsn': env('SENTRY_DSN'),
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        'release': raven.fetch_git_sha(str(ROOT_DIR)),
    }

if env.bool('DJANGO_USE_DEBUG_TOOLBAR'):
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )
    INSTALLED_APPS += ('debug_toolbar', )
    DEBUG_TOOLBAR_CONFIG = {
        'DISABLE_PANELS': [
            'debug_toolbar.panels.redirects.RedirectsPanel',
        ],
        'SHOW_TEMPLATE_CONTEXT': True,
    }
