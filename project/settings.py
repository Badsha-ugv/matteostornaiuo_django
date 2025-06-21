import os
from pathlib import Path
import dj_database_url
from decouple import config

from dotenv import load_dotenv
from datetime import timedelta
from import_export.formats.base_formats import CSV, XLSX

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


from .unfold import UNFOLD
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-m$w8san7%avlpm*x2n7ing8mri-c&wh!4wfody(30se_x2mln^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['admin.letme.no', '*']


INSTALLED_APPS = [
    "daphne",
    "unfold",  
    "unfold.contrib.filters", 
    "unfold.contrib.forms", 
    "unfold.contrib.inlines",  
    "unfold.contrib.import_export",  
    "unfold.contrib.guardian", 
    "unfold.contrib.simple_history",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # 3rd party 
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework_simplejwt",
    "storages",

    #local
    "import_export",
    "drf_spectacular",
    "corsheaders",
    'whitenoise.runserver_nostatic',
    "homedashbord",
    "celeryapi",
    "users",
    "client",
    "staff",
    "dashboard",
    "chat",
    "shifting",
    "subscription",



]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # custom middleware
    "querycount.middleware.QueryCountMiddleware",

]


# Rest framework
REST_FRAMEWORK = {
    # for auth
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # session authentication
        "rest_framework.authentication.SessionAuthentication",
        # basic authentication
        "rest_framework.authentication.BasicAuthentication",
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # pagination 
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "project.asgi.application"
# WSGI_APPLICATION = "project.wsgi.application"





# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'matteostornaiuo',
        'USER': 'matteostornaiuo',
        'PASSWORD': 'matteostornaiuo@AA',
        'HOST': '16.16.199.236',
        'PORT': '5432',
    }
}

# channels - redis configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],  # Redis server configuration
        },
    },
}


CELERY_BROKER_URL = 'redis://localhost:6379/0' 
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_TIMEZONE = 'UTC'
USE_TZ = True


SPECTACULAR_SETTINGS = {
    'TITLE': 'Matteo API',
    'DESCRIPTION': 'API documentation',
    'VERSION': '1.0.0',
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]



LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True




STATIC_URL = "/static/"
STATICFILE_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:8080',

    'https://dev.letme.no',
    'https://www.dev.letme.no',
]
# CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:8080',

    'https://dev.letme.no',
    'https://www.dev.letme.no',
]
# SESSION_COOKIE_SECURE = True  # Ensure cookies are only sent over HTTPS
# CSRF_COOKIE_SECURE = True  # Ensure CSRF cookies are only sent over HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# multiple import options
IMPORT_FORMATS = [CSV, XLSX]
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# for auth
AUTH_USER_MODEL = "users.User"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'BLACKLIST_AFTER_ROTATION': True,
    "ROTATE_REFRESH_TOKENS": True,
}



# email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = "mainbsl4@gmail.com"
EMAIL_HOST_PASSWORD = "nmwk umma atdu sosv"
EMAIL_PORT = 465  
EMAIL_USE_SSL = True


# Stripe settings (Badsha)
STRIPE_PUBLIC_KEY = "pk_test_51MhVdoSI80DUGvJVmqHGBD9DUrbFnouO2ikPJxyWj4tpELlnViPbK2niqEgmxDvmXwjiUqNHzMXs8sfQsoW6RNM700HLRJ0ekb"
STRIPE_SECRET_KEY  = "sk_test_51MhVdoSI80DUGvJV2cJX44q7luc0y6updGFvyxOR5kG6blPQk2AXXg5QNNyWn7hBU8k3u6oZEDlufGbaD6ytufcJ00n6mgp4Os"
# STRIPE_WEBHOOK_SECRET = "whsec_3fbae828a232d2c22cfbe6e170fb1d26869fca7e6d3bf66acb81390e20a3f204"
STRIPE_WEBHOOK_SECRET = "whsec_zl0AWrt8NfVlknmJ2mTEBVYRY0HZtBz4"

STRIPE_SUCCESS_URL = "http://localhost:5173/success"
STRIPE_CANCEL_URL = "http://localhost:5173/cancel"





# AWS S3 settings
# AWS Configuration
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME")

AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"

# Configure Django-Storages
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_DEFAULT_ACL = 'public-read'
AWS_DEFAULT_ACL = None




# inmemory cache backend
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}


# celety configuration
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'