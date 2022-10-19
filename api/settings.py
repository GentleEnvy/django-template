# imports

import importlib
from functools import partial
import logging
import os
from pathlib import Path

# noinspection PyPackageRequirements
import environ

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from app.base.logs.configs import LogConfig

# env

_env_value = {'value': lambda s: s.split(',')}

env = environ.Env(
    WEB_DOMAIN=(str, 'local.dev'),
    API_DOMAIN=(str, 'api.local.dev'),
    SECRET_KEY=(str, 'secret'),
    DEBUG=(bool, True),
    TEST=(bool, False),
    ANON_THROTTLE_RATE=(str, '1000/s'),
    USER_THROTTLE_RATE=(str, '10000/s'),
    VERIFICATION_CODE_TIMEOUT=(int, 86400),
    VERIFICATION_ACTIVATE_SUCCESS_PATH=(str, '#!/activate/success?token=%s'),
    VERIFICATION_ACTIVATE_FAILURE_PATH=(str, '#!/activate/failure'),
    VERIFICATION_PASSWORD_SUCCESS_PATH=(str, '#!/password/success?session_id=%s'),
    VERIFICATION_PASSWORD_FAILURE_PATH=(str, '#!/password/failure'),
    EMAIL_BACKEND=(str, None),  # default: 'console' if DEBUG else 'smtp'
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
    CELERY_REDIS_MAX_CONNECTIONS=(int, 2),
    CELERY_BROKER_POOL_LIMIT=int,  # default: CELERY_REDIS_MAX_CONNECTIONS
    CELERY_TASK_EAGER=(bool, False),
    SESSION_ON_LOGIN=bool,  # default: DEBUG
    USE_SILKY=bool,  # default: DEBUG
    CLOUDINARY_URL=(str, None),
    SENTRY_DSN=(str, None),
)

# root

BASE_DIR = environ.Path(__file__) - 2

WSGI_APPLICATION = 'api.wsgi.application'
ASGI_APPLICATION = 'api.asgi.application'
ROOT_URLCONF = 'api.urls'

# site

SITE_NAME = 'Dev'
SITE_ROOT = BASE_DIR
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
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'django_cleanup',
    'django_pickling',
    'cacheops',
    'silk',
    'cloudinary',
    'cloudinary_storage',
    'drf_spectacular',
    'django_celery_beat',
    'djcelery_email',
    # own apps
    'app.base',
    'app.users',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'app.base.renderers.ORJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'app.base.parsers.ORJSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'app.base.authentications.token.TokenAuthentication',
        'app.base.authentications.session.SessionAuthentication',
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
    'corsheaders.middleware.CorsMiddleware',  # should be as high as possible
    # django middlewares
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # third-party middlewares
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'silk.middleware.SilkyMiddleware',
    # own middlewares
    'app.base.middlewares.log.LogMiddleware',
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
    'timeout': 60 * 60,
    'cache_on_save': True,
    'ops': ['get', 'fetch', 'exists', 'count'],
}
CACHEOPS = {'authtoken.*': {}, 'users.*': {}}

CACHEOPS_DEGRADE_ON_FAILURE = True

# email

EMAIL_HOST: str | None = None
EMAIL_PORT: int | None = None
EMAIL_USE_SSL: bool | None = None
EMAIL_HOST_USER: str | None = None
EMAIL_HOST_PASSWORD: str | None = None
EMAIL_BACKEND: str | None = None

try:
    vars().update(
        env.email('EMAIL_URL', backend='djcelery_email.backends.CeleryEmailBackend')
    )
except environ.ImproperlyConfigured:
    pass

# celery_email

CELERY_EMAIL_BACKEND = (
    f"django.core.mail.backends."
    f"{env('EMAIL_BACKEND') or 'console' if DEBUG else 'smtp'}.EmailBackend"
)
CELERY_EMAIL_TASK_CONFIG = {'name': None, 'ignore_result': False}
CELERY_EMAIL_CHUNK_SIZE = 1

# verification

VERIFICATION_CODE_TIMEOUT = env('VERIFICATION_CODE_TIMEOUT')
VERIFICATION_ACTIVATE_SUCCESS_URL: str = (
    f"https://{WEB_DOMAIN}{env('VERIFICATION_ACTIVATE_SUCCESS_PATH')}"
)
VERIFICATION_ACTIVATE_FAILURE_URL: str = (
    f"https://{WEB_DOMAIN}{env('VERIFICATION_ACTIVATE_FAILURE_PATH')}"
)
VERIFICATION_PASSWORD_SUCCESS_URL: str = (
    f"https://{WEB_DOMAIN}{env('VERIFICATION_PASSWORD_SUCCESS_PATH')}"
)
VERIFICATION_PASSWORD_FAILURE_URL: str = (
    f"https://{WEB_DOMAIN}{env('VERIFICATION_PASSWORD_FAILURE_PATH')}"
)

# celery[broker]

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=REDIS_URL)

CELERY_TASK_ALWAYS_EAGER = env('CELERY_TASK_EAGER')
CELERY_TASK_ANNOTATIONS = {'*': {'rate_limit': '10/s'}}
CELERY_TASK_COMPRESSION = 'gzip'
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 12 * 60 * 60,
    'max_connections': env('CELERY_REDIS_MAX_CONNECTIONS'),
    'socket_keepalive': True,
}
CELERY_BROKER_POOL_LIMIT = env(
    'CELERY_BROKER_POOL_LIMIT', default=env('CELERY_REDIS_MAX_CONNECTIONS')
)
CELERY_TRACK_STARTED = True
CELERY_TASK_SERIALIZER = 'json'

# celery[result]

CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=REDIS_URL)

CELERY_RESULT_COMPRESSION = CELERY_TASK_COMPRESSION
CELERY_RESULT_ACCEPT_CONTENT = ['json']
CELERY_IGNORE_RESULT = False

# celery beat

CELERY_BEAT_SCHEDULE = {}

# media

if (CLOUDINARY_URL := env('CLOUDINARY_URL')) is not None:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR + 'media'
DATA_UPLOAD_MAX_MEMORY_SIZE = None

# static

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + 'static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# silk

USE_SILKY = env('USE_SILKY', default=DEBUG)

SILKY_INTERCEPT_FUNC = lambda _: USE_SILKY
SILKY_META = True
SILKY_ANALYZE_QUERIES = True
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_PYTHON_PROFILER_RESULT_PATH = BASE_DIR + 'profiles/'
if not os.path.exists(SILKY_PYTHON_PROFILER_RESULT_PATH):
    os.makedirs(SILKY_PYTHON_PROFILER_RESULT_PATH)

SILKY_MAX_RECORDED_REQUESTS = 1_000
SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 50

# sentry

if (SENTRY_DSN := env('SENTRY_DSN')) is not None:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            LoggingIntegration(
                level=logging.DEBUG,
                event_level=logging.ERROR,
            ),
            DjangoIntegration(),
            RedisIntegration(),
        ],
        environment={True: 'Dev', False: 'Prod'}[DEBUG],
        traces_sample_rate=1,
    )

# swagger

SPECTACULAR_SETTINGS = {
    'TITLE': f'{SITE_NAME} API',
    'VERSION': '1.0',
    'DISABLE_ERRORS_AND_WARNINGS': not DEBUG,
}

# db

DATABASES = {'default': env.db()}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# auth

AUTH_USER_MODEL = 'users.User'
SESSION_ON_LOGIN = env('SESSION_ON_LOGIN', default=DEBUG)

# password

PASSWORD_HASHERS = ['app.base.hashers.argon2.Argon2PasswordHasher']

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# logs

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
