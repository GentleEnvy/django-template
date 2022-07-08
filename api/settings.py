# imports

import base64
import importlib
from functools import partial
from pathlib import Path

# noinspection PyPackageRequirements
import environ
from pybase64 import b64decode, b64encode

from app.base.logs.configs import LogConfig

base64.b64encode = b64encode
base64.b64decode = b64decode

# env

_env_value = {'value': lambda s: s.split(',')}

env = environ.Env(
    SITE_NAME=(str, 'dev'),
    WEB_DOMAIN=(str, 'local.dev'),
    API_DOMAIN=(str, 'api.local.dev'),
    SECRET_KEY=(str, 'secret'),
    DEBUG=(bool, True),
    TEST=(bool, False),
    ANON_THROTTLE_RATE=(str, '1000/s'),
    USER_THROTTLE_RATE=(str, '10000/s'),
    VERIFICATION_CODE_TIMEOUT=(int, 86400),
    VERIFICATION_ACTIVATE_SUCCESS_URL=(
        str,
        'https://local.dev#!/activate/success?token=%s',
    ),
    VERIFICATION_ACTIVATE_FAILURE_URL=(str, 'https://local.dev#!/activate/failure'),
    VERIFICATION_PASSWORD_SUCCESS_URL=(
        str,
        'https://local.dev#!/password/success?session=%s',
    ),
    VERIFICATION_PASSWORD_FAILURE_URL=(str, 'https://local.dev#!/password/failure'),
    EMAIL_BACKEND=(str, None),
    LOG_CONF=(_env_value, {'api': ['api_console'], 'django.server': ['web_console']}),
    LOG_PRETTY=(bool, True),
    LOG_MAX_LENGTH=(int, 130),
    LOG_FORMATTERS=(
        dict,
        {
            'api': (
                '%(levelname)-8s| %(name)s %(asctime)s <%(module)s->%(funcName)s(%('
                'lineno)d)>: %(message)s'
            ),
            'web': 'WEB     | %(asctime)s: %(message)s',
        },
    ),
    LOG_LEVEL=(dict, {}),
    CELERY_REDIS_MAX_CONNECTIONS=(int, 10),
    ADMINS=(_env_value, {}),
    CLOUDINARY_URL=(str, None),
)

# root

SETTINGS_PATH = environ.Path(__file__)
BASE_DIR = SETTINGS_PATH - 2

WSGI_APPLICATION = (SETTINGS_PATH - 1)().split('\\')[-1].split('/')[-1] + (
    '.wsgi.application'
)
ROOT_URLCONF = (SETTINGS_PATH - 1)().split('\\')[-1].split('/')[-1] + '.urls'

# site

SITE_ROOT = BASE_DIR
SITE_NAME = env('SITE_NAME')
WEB_DOMAIN = env('WEB_DOMAIN')
API_DOMAIN = env('API_DOMAIN')
DOMAIN = WEB_DOMAIN

# django

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
TEST = env('TEST')

INSTALLED_APPS = [
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    # third-party apps
    'django_filters',
    'django_cleanup',
    'django_pickling',
    'django_celery_beat',
    'djcelery_email',
    'cacheops',
    'cloudinary',
    'cloudinary_storage',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'corsheaders',
    *(['debug_toolbar'] if DEBUG else []),
    # own apps
    'app.base',
    'app.users',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'drf_orjson_renderer.renderers.ORJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': ['drf_orjson_renderer.parsers.ORJSONParser'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'app.users.authentications.token.TokenAuthentication',
        'app.users.authentications.session.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'app.base.paginations.base.BasePagination',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': env('ANON_THROTTLE_RATE'),
        'user': env('USER_THROTTLE_RATE'),
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

MIDDLEWARE = [
    # django middlewares
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # third-party middlewares
    'whitenoise.middleware.WhiteNoiseMiddleware',
    *(['debug_toolbar.middleware.DebugToolbarMiddleware'] if DEBUG else []),
    # own middlewares
    'app.base.middlewares.RequestLogMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        },
    }
]

# allow

ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
INTERNAL_IPS = ['127.0.0.1']

# cache

CACHES = {
    'default': {
        **(_default_cache := env.cache('REDIS_URL')),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    }
}

REDIS_URL = _default_cache['LOCATION']

# cacheops

CACHEOPS_REDIS = REDIS_URL

CACHEOPS_DEFAULTS = {
    'timeout': 60 * 5,
    'cache_on_save': True,
    'ops': ['get', 'fetch', 'exists'],
}
CACHEOPS = {'authtoken.*': {}, 'users.*': {}}

CACHEOPS_DEGRADE_ON_FAILURE = True

# email

EMAIL_HOST: str
EMAIL_PORT: int
EMAIL_USE_SSL: bool
EMAIL_HOST_USER: str
EMAIL_HOST_PASSWORD: str
EMAIL_BACKEND: str

vars().update(
    env.email('EMAIL_URL', backend='djcelery_email.backends.CeleryEmailBackend')
)

# verification

VERIFICATION_CODE_TIMEOUT = env('VERIFICATION_CODE_TIMEOUT')
VERIFICATION_ACTIVATE_SUCCESS_URL = env('VERIFICATION_ACTIVATE_SUCCESS_URL')
VERIFICATION_ACTIVATE_FAILURE_URL = env('VERIFICATION_ACTIVATE_FAILURE_URL')
VERIFICATION_PASSWORD_SUCCESS_URL = env('VERIFICATION_PASSWORD_SUCCESS_URL')
VERIFICATION_PASSWORD_FAILURE_URL = env('VERIFICATION_PASSWORD_FAILURE_URL')

# celery_email

CELERY_EMAIL_BACKEND = (
    f"django.core.mail.backends."
    f"{env('EMAIL_BACKEND') or 'console' if DEBUG else 'smtp'}.EmailBackend"
)
CELERY_EMAIL_TASK_CONFIG = {'name': None, 'ignore_result': False}
CELERY_EMAIL_CHUNK_SIZE = 1

# celery

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=REDIS_URL)
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=REDIS_URL)

CELERY_REDIS_MAX_CONNECTIONS = env('CELERY_REDIS_MAX_CONNECTIONS')
CELERY_REDIS_SOCKET_KEEPALIVE = True

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 20,
    'max_connections': CELERY_REDIS_MAX_CONNECTIONS,
    'socket_keepalive': True,
}
CELERY_BROKER_POOL_LIMIT = 0

CELERY_RESULT_SERIALIZER = 'json'

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = False
CELERY_TRACK_STARTED = True

CELERY_BEAT_SCHEDULE = {}

# media

MEDIA_URL = '/media/'
DATA_UPLOAD_MAX_MEMORY_SIZE = None

CLOUDINARY_URL = env('CLOUDINARY_URL')
if CLOUDINARY_URL:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# static

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# swagger

SPECTACULAR_SETTINGS = {
    'TITLE': f'{SITE_NAME} API',
    'VERSION': '1.0',
    'DISABLE_ERRORS_AND_WARNINGS': DEBUG,
}

# db

DATABASES = {'default': env.db()}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# auth

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.User'
SESSION_ON_LOGIN = env('SESSION_ON_LOGIN', bool, DEBUG)

# logs

LOG_ADMINS = {
    v[0]: list(map(lambda s: s.lower(), v[1:])) for v in env('ADMINS').values()
}
ADMINS = [(name, email__levels[0]) for name, email__levels in env('ADMINS').items()]
EMAIL_SUBJECT_PREFIX = f'{SITE_NAME} logger > '

LOG_FORMATTERS = env('LOG_FORMATTERS')
LOG_PRETTY = env('LOG_PRETTY')
LOG_MAX_LENGTH = env('LOG_MAX_LENGTH')

_loggers = {
    k: {
        'handlers': list(
            map(
                partial(
                    getattr,
                    importlib.import_module('.handlers', 'app.base.logs.configs'),
                ),
                v,
            )
        )
    }
    for k, v in env('LOG_CONF').items()
}
for k, v in env('LOG_LEVEL').items():
    _loggers.setdefault(k, {})['level'] = v

LOGGING = LogConfig(_loggers).to_dict()

# language

USE_I18N = True

# timezone

TIME_ZONE = 'UTC'
USE_L10N = True
USE_TZ = True
