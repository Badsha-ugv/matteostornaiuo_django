from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from pathlib import Path
import os
from datetime import timedelta
import dj_database_url
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv



load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-m$w8san7%avlpm*x2n7ing8mri-c&wh!4wfody(30se_x2mln^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['admin.letme.no', '*']


INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history", # optional, if django-simple-history package is used
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework_simplejwt",
    "storages",
    "users",
    "client",
    "staff",
    "dashboard",
    "chat",
    "shifting",
    "subscription",
    # 3rd party 
    "import_export",
    "drf_spectacular",
    "corsheaders",
    'whitenoise.runserver_nostatic',
    "homedashbord",
    "celeryapi",


    
    

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

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     'default': dj_database_url.config(
#         default='postgresql://matteo:YhG2Qs5c5I92yle0O7jFH9AVa6PsZ4f7@dpg-cujej9ggph6c73bev3p0-a.oregon-postgres.render.com/matteo'
#     )
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'matteostornaiuo',
        'USER': 'matteostornaiuo',
        'PASSWORD': 'matteostornaiuo@AA',
        'HOST': '13.53.162.107',
        'PORT': '5432',
    }
}

# DATABASES = {
#     'default': dj_database_url.config(
#         default='postgresql://matteo:YhG2Qs5c5I92yle0O7jFH9AVa6PsZ4f7@dpg-cujej9ggph6c73bev3p0-a.oregon-postgres.render.com/matteo'
#     )
# }


CELERY_BROKER_URL = 'redis://localhost:6379/0' 
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_TIMEZONE = 'UTC'
USE_TZ = True


SPECTACULAR_SETTINGS = {
    'TITLE': 'Matteo API',
    'DESCRIPTION': 'API documentation',
    'VERSION': '1.0.0',
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILE_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:8080',

    'https://letme-frontend-web.netlify.app',
    'https://letme.no',
    'https://www.letme.no',
    'https://test.letme.no',
    'https://www.test.letme.no',
]
# CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:8080',

    'https://www.letme.no',
    'https://letme.no'
    'https://test.letme.no',
    'https://www.test.letme.no',
]
# SESSION_COOKIE_SECURE = True  # Ensure cookies are only sent over HTTPS
# CSRF_COOKIE_SECURE = True  # Ensure CSRF cookies are only sent over HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

from import_export.formats.base_formats import CSV, XLSX
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


# Stripe settings
STRIPE_PUBLIC_KEY = "pk_test_51MhVdoSI80DUGvJVmqHGBD9DUrbFnouO2ikPJxyWj4tpELlnViPbK2niqEgmxDvmXwjiUqNHzMXs8sfQsoW6RNM700HLRJ0ekb"
STRIPE_SECRET_KEY  = "sk_test_51MhVdoSI80DUGvJV2cJX44q7luc0y6updGFvyxOR5kG6blPQk2AXXg5QNNyWn7hBU8k3u6oZEDlufGbaD6ytufcJ00n6mgp4Os"
# STRIPE_WEBHOOK_SECRET = "whsec_3fbae828a232d2c22cfbe6e170fb1d26869fca7e6d3bf66acb81390e20a3f204"
STRIPE_WEBHOOK_SECRET = "we_1QtNiWSI80DUGvJVPLfqoT0H"

STRIPE_SUCCESS_URL = "http://127.0.0.1:8080/success"
STRIPE_CANCEL_URL = "http://127.0.0.1:8080/cancel"





# AWS S3 settings
# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')

AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"

# Configure Django-Storages
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_DEFAULT_ACL = 'public-read'
AWS_DEFAULT_ACL = None







# celety configuration
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'



UNFOLD = {
    
    
    "DASHBOARD_CALLBACK": "homedashbord.views.dashboard_callback",

     "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True, 
         
         "navigation": [
            {
                "title": _("Super Admin"), 
                "separator": True,  # Top border
                "collapsible": False, 
                "SITE_TITLE": "Letme Administrator",
                "SITE_HEADER": "Letme Admin Dashboard",
                # "SITE_SUBHEADER": "Appears under SITE_HEADER",
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        # "badge": "homedashbord.views.available_staff_badge",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": _("Job Role"),
                        "icon": "engineering",
                        "link": reverse_lazy("admin:users_jobrole_changelist"),
                    },
                    {
                        "title": _("Skills"),
                        "icon": "bolt",
                        "link": reverse_lazy("admin:users_skill_changelist"),
                    },
                    {
                        "title": _("Uniform"),
                        "icon": "person_apron",
                        "link": reverse_lazy("admin:users_uniform_changelist"),
                    },
                    {
                        "title": _("Notifications"),
                        "icon": "notifications_active",
                        "link": reverse_lazy("admin:dashboard_notification_changelist"),
                    },
                    {
                        "title": _("Report and Issue"),
                        "icon": "flag",
                        "link": reverse_lazy("admin:dashboard_report_changelist"),
                    },
                    {
                    "title": _("FAQ"),
                        "icon": "contact_support",
                        "link": reverse_lazy("admin:dashboard_faq_changelist"),
                    },
                    {
                    "title": _("Terms and Conditions"),
                        "icon": "description",
                        "link": reverse_lazy("admin:dashboard_termsandconditions_changelist"),
                    },
                ],
            },
            {
                "title": _("Company Profile"),
                "icon": "apartment",
                "collapsible": False, 
                "items":[
                    {
                        "title": _("Profile"),
                        "icon": "apartment",
                        "link": reverse_lazy("admin:client_companyprofile_changelist"),
                    },
                    {
                        "title": _("Jobs"),
                        "icon": "work",
                        "link": reverse_lazy("admin:client_job_changelist"),
                    },
                    {
                        "title": _("Vacancies"),
                        "icon": "work",
                        "link": reverse_lazy("admin:client_vacancy_changelist"),
                    },
                    {
                        "title": _("Checkin"),
                        "icon": "check",
                        "link": reverse_lazy("admin:client_checkin_changelist"),
                    },
                    {
                        "title": _("Checkout"),
                        "icon": "done_all",
                        "link": reverse_lazy("admin:client_checkout_changelist"),
                    },
                    {
                        "title": _("Favourite Staff"),
                        "icon": "star",
                        "link": reverse_lazy("admin:client_favouritestaff_changelist"),
                    },
                    {
                        "title": _("My Own Staff"),
                        "icon": "location_away",
                        "link": reverse_lazy("admin:client_mystaff_changelist"),
                    },
                    {
                        "title": _("Job Ads"),
                        "icon": "ads_click",
                        "link": reverse_lazy("admin:client_jobads_changelist"),
                    },
                    {
                        "title": _("Job Application"),
                        "icon": "inventory",
                        "link": reverse_lazy("admin:client_jobapplication_changelist"),
                    },
                    {
                        "title": _("Job Report"),
                        "icon": "work_history",
                        "link": reverse_lazy("admin:client_jobreport_changelist"),
                    },
                    {
                        "title": _("Review"),
                        "icon": "reviews",
                        "link": reverse_lazy("admin:client_companyreview_changelist"),
                    }
                ]
            },
            {
                "title": _("Staff Profile"),
                "icon": "apartment",
                "collapsible": False, 
                "items":[
                    {
                        "title": _("Staff"),
                        "icon": "id_card",
                        "badge": "homedashbord.views.available_staff_badge",
                        "link": reverse_lazy("admin:staff_staff_changelist"),
                    },
                    {
                        "title": _("Experiences"),
                        "icon": "emoji_objects",
                        "link": reverse_lazy("admin:staff_experience_changelist"),
                    },
                    {
                        "title": _("Review"),
                        "icon": "reviews",
                        "link": reverse_lazy ("admin:staff_staffreview_changelist"),
                    }
                ]
            },
            
        ],
    },

    "STYLES": [
        lambda request: static("css/custom_unfold.css"),
    ],

    "SCRIPTS": [
        lambda request: static("js/custom_unfold.js"),
        lambda request: static("js/pie_chart_unfold.js"),
    ],

}

