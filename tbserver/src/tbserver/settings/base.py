"""
Tezbor Service Settings
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(__file__)

SECRET_KEY = 'django-insecure-s#@w&=hv8h+1g*v13rzafrzn2l)ttvk7vq2v2yyuevv-x7w+^!'

DEBUG = True

DEFAULT_ACTIVATION_TIME = 3

ALLOWED_HOSTS = ["tezbor.uz", "127.0.0.1"]

AUTH_USER_MODEL = 'accounts.User'  # use our custom User model (not Django's)

# Application definition
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third-party apps
    'corsheaders',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'storages',
    'coreapi',
    'drf_yasg',
    # 'fcm_django',
    'channels',

    'apps.accounts',
    'apps.addresses',
    'apps.billing',
    'apps.orders',
    'apps.queues',
    'apps.uploads',
    'apps.dashboard',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tbserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    #'DATETIME_FORMAT': "%Y-%m-%d %H:%M",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES':
        ('rest_framework.permissions.AllowAny',),
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     'rest_framework_simplejwt.authentication.JWTAuthentication',
    #     'rest_framework.authentication.SessionAuthentication',
    # ),

    # 'EXCEPTION_HANDLER': 'apps.core.services.exceptions.core_exception_handler',
    # 'NON_FIELD_ERRORS_KEY': 'error',

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# SWAGGER_SETTINGS = {
#     'USE_SESSION_AUTH': False
# }

SWAGGER_SETTINGS = {
    'exclude_url_names': [],
    'exclude_namespaces': [],
    'api_version': '0.1',
    'api_path': '/',
    'relative_paths': False,
    'enabled_methods': [
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    'api_key': '',
    'is_authenticated': False,
    'is_superuser': False,
    'unauthenticated_user': 'django.contrib.auth.models.AnonymousUser',
    'permission_denied_handler': None,
    'resource_access_handler': None,
    'base_path': 'helloreverb.com/docs',
    'info': {
        'contact': 'apiteam@wordnik.com',
        'description': 'This is a sample server Petstore server. '
                       'You can find out more about Swagger at '
                       '<a href="https://swagger.wordnik.com">https://swagger.wordnik.com</a> '
                       'or on irc.freenode.net, #swagger. '
                       'For this sample, you can use the api key '
                       '"special-key" to test '
                       'the authorization filters',
        'license': 'Apache 2.0',
        'licenseUrl': 'https://www.apache.org/licenses/LICENSE-2.0.html',
        'termsOfServiceUrl': 'https://helloreverb.com/terms/',
        'title': 'Swagger Sample App',
    },
    'DEFAULT_FIELD_INSPECTORS': [
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.InlineSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
    'doc_expansion': 'none',
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
}

WSGI_APPLICATION = 'tbserver.wsgi.application'
ASGI_APPLICATION = 'tbserver.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# configure Djoser
DJOSER = {
    "USER_ID_FIELD": "phone_number"
}

LOGIN_URL = "login"

BLACKLISTED_USERS = ["+998552277407", "+998555005051", "+998555005055"]

PYFCM_CUSTOMER_SERVER_KEY = "AAAAAbdAnJk:APA91bHfO9v0BlObM5R117-9MFUaa02fYWrJiN3vsv5EPQNXXnQHVjhLNYQwxtAgtqNBEpCoAxrkY97J8fdVzTNCMU7PW7gJyCwnHV0a6dLC83MeaJoU_r1oX6I7-rxWStJ8YjSFOioI"
PYFCM_AGENT_SERVER_KEY = "AAAAU2-8bjw:APA91bFUKDohLkTr8AHUK1BbiIFMl8Myksso2oFSTf0Iq-rg-UGO545f7T-tZwjOmMUwVlOCvJJofqP1YFWw5ysyEKvZqvTVUYvCADMA9luZ_apUPHcxz0jKtFEfwMUCjw7rWalMWCXQ"
PYFCM_DRIVER_SERVER_KEY = "AAAAPwJIMrk:APA91bHAa3uAPk5gULC1haSgz8Szws3BT13HdGOrGg9Ktvf8gxcUxu_S4kcPMaZhcW82AN0DoEbEcXJYTOp24a7lvjh0SZi1yCmdiOr7Fsz6Q3SPwqxOOx3RKaICkf47Bx1JPpdn13st"

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# STATIC_ROOT = (os.path.join(BASE_DIR, 'static'))

gettext = lambda s: s
LANGUAGES = (
    ('uz', gettext('Uzbek')),
    ('en', gettext('English')),
    ('ru', gettext('Russian')),
)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_WHITELIST = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:8080",
                         "https://api.tezbor.uz", "https://www.api.tezbor.uz", "https://tezbor.uz",
                         "https://tezbor.magician.casa", "http://192.168.0.100", "https://gobazar.uz",
                         "https://opencart.kelajakimorat.uz", "https://kitoblardunyosi.uz",
                         "http://opencart.kelajakimorat.uz", "http://kitoblardunyosi.uz",
                         "http://test.uz"]


redis_host = os.environ.get('REDIS_HOST', 'src_redis_1')

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(redis_host, 6379)],
        },
    },
}

HAMYON_USERNAME = os.environ.get("HAMYON_USERNAME", "something_different")
HAMYON_PASSWORD = os.environ.get("HAMYON_PASSWORD", "something_different")
HAMYON_BASE_URL = os.environ.get("HAMYON_BASE_URL", "something_different")

SG_API_KEY = os.environ.get("SENDGRID_API_KEY", "Change me")
TB_NO_REPLY_EMAIL = os.environ.get("NO_REPLY_EMAIL", "Change me")
TB_SUPPORT_EMAIL = os.environ.get("SUPPORT_EMAIL", "Change me")