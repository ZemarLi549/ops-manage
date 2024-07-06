"""
Django settings for ops_manage project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j9y3x$8irr$3*(kcyu!j-ar2w*6=%rku7+gt_gy%$p%cim(3!5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
LOGLEVEL = os.environ.get('LOGLEVEL','INFO')

ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# CORS_ALLOW_HEADERS = (
#     '*',
#     "Origin",
#     "X-Requested-With",
#     "Content-Type",
#     "Accept",
#     "Authorization",
# )

APPNAME = 'ops_manage'

BASE_URL = os.environ.get('BASE_URL', "ops-manage/v1/")
# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django_filters',
    'rest_framework',
    'drf_yasg',
    'apps.management',
    'apps.om_auth',
    'apps.om_logsearch',
    'apps.om_alarm',
    'captcha',
    'channels'
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.management.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'apps.om_auth.views.LoginAuth',
]

ROOT_URLCONF = 'ops_manage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # 'django.contrib.management.context_processors.management',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ops_manage.wsgi.application'
ASGI_APPLICATION = "ops_manage.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

MYSQL_DB_NAME = os.environ.get('MYSQL_DB_NAME', 'ops_manage')
MYSQL_DB_USER = os.environ.get('MYSQL_DB_USER', 'root')
MYSQL_DB_PASSWD = os.environ.get('MYSQL_DB_PASSWD', 'piecelovewudi')
MYSQL_DB_HOST = os.environ.get('MYSQL_DB_HOST', '10.110.1.17')
MYSQL_DB_PORT = os.environ.get('MYSQL_DB_PORT', '3307')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQL_DB_NAME,
        'USER': MYSQL_DB_USER,
        'PASSWORD': MYSQL_DB_PASSWD,
        'HOST': MYSQL_DB_HOST,
        'PORT': MYSQL_DB_PORT,
    }
}




# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


STATIC_URL = '/static/'

STATIC_ROOT = 'static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # 设置Gzip压缩

LOGPATH = f'/data/applications/{APPNAME}/logs'
LOGPATH = os.environ.get('LOGPATH', LOGPATH)
if not os.path.exists(LOGPATH):
    os.makedirs(LOGPATH)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            # 'format': "%(asctime)s %(msecs)03d [%(levelname)s ] %(process)s %(pathname)s %(lineno)d - %(message)s",
            'format': "[%(asctime)s.%(msecs)03d] [%(filename)s:%(lineno)d] [%(levelname)s] - [%(message)s]",
            "datefmt":"%Y-%m-%d %H:%M:%S"
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'default': {
            'level': LOGLEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '%s/%s.log' % (LOGPATH, APPNAME),
            'backupCount': 10, # keep at most 10 log files
            'maxBytes': 52428800, # 100*1024*1024 bytes (5MB)
            'formatter': 'standard'
        },
        'console': {
            'level': LOGLEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            # 'filters': ['require_debug_false'],
        },
        'request_handler': {
            'level': LOGLEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '%s/request.log' % LOGPATH,
            'formatter': 'standard',
            'maxBytes': 52428800 # 100*1024*1024 bytes (5MB)
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '%s/error.log' % LOGPATH,
            'backupCount': 10,
            'maxBytes': 52428800, # 100*1024*1024 bytes (5MB)
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default', 'console', 'error'],
            'level': LOGLEVEL,
            'propagate': True
        },
        'django.request': {
            'handlers': ['default', 'request_handler', 'error'],
            'level': LOGLEVEL,
            'propagate': False,
        },
        'ops_manage': {
            'handlers': ['default', "console", 'error'],
            'level': LOGLEVEL,
            'propagate': True
        },
        'apps': {
            'handlers': ['default', 'console', 'error'],
            'level': LOGLEVEL,
            'propagate': True
        },
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.management` permissions,
    # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'common.permissions.IsOrgAdmin',
    # ),
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer',
    #     'common.renders.JMSCSVRender',
    # ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        # 'common.parsers.JMSCSVParser',
        'rest_framework.parsers.FileUploadParser',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    # 'DEFAULT_METADATA_CLASS': 'common.drfmetadata.SimpleMetadataWithFilters',
    'ORDERING_PARAM': "order",
    'SEARCH_PARAM': "search",
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
    'DATETIME_INPUT_FORMATS': ['iso-8601', '%Y-%m-%d %H:%M:%S'],
    #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.CustomPagination',
    # 'PAGE_SIZE': 15
}

#swagger
SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/login',
    'LOGOUT_URL': '/admin/logout',
    'PERSIST_AUTH': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'REFETCH_SCHEMA_ON_LOGOUT': True,
    "FETCH_SCHEMA_WITH_QUERY": True,
    "SHOW_COMMON_EXTENSIONS": True,
    # 'DEFAULT_INFO': 'ops_management.urls.swagger_info',#这里注意，更改为自己的项目路径
    # 'DEFAULT_AUTO_SCHEMA_CLASS': 'apps.swagger.CustomSwaggerAutoSchema',
    'DEFAULT_INFO': 'apps.swagger.api_info',
    'SECURITY_DEFINITIONS': {
        # 'Basic': {
        #     'type': 'basic'
        # },
        'Bearer': {
            'type': 'apiKey',
            'name': 'x-token',
            'in': 'header'
        },
        # 'Query': {
        #     'type': 'apiKey',
        #     'name': 'management',
        #     'in': 'query'
        # },
    }
}

#ladp
AD_SERVER = 'ldap://ldap.eops.com:389'
AD_BIND_DN = "cn=techblog,ou=people,dc=eops,dc=com"
AD_BASE_DN = 'ou=people,dc=eops,dc=com'
AD_PASSWORD = '123456'
# session 设置

TOKEN_AGE=3600*24*7
JWT_SECRET=SECRET_KEY

# SESSION_COOKIE_AGE = 60 * 180 # 180分钟
# SESSION_SAVE_EVERY_REQUEST = True
# SESSION_EXPIRE_AT_BROWSER_CLOSE = False # 关闭浏览器，则COOKIE失效
RELEASE_KEY = os.environ.get("RELEASE_KEY", "kn6xCoKsNkdMvwDOwmyiYgsyL6y7J0i4I74-_2ZBwMI=")
#auth WHITE_URL_LIST
WHITE_URL_LIST = ['login','swagger','token','captcha','register','alert','identity_info','alarm_query','solution','comment','alarmexist','alarmsimilar']

#redis
TIME_ZONE = 'Asia/Shanghai'
REDIS_HOST=os.environ.get('REDIS_HOST','10.110.1.17')
REDIS_PASSWORD=os.environ.get('REDIS_PASSWORD','pieceloveredis')
REDIS_PORT=os.environ.get('REDIS_PORT',6380)
REDIS_DB=os.environ.get('REDIS_DB',10)
#CELERY TASKS
BROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_BROKER_URL = BROKER_URL
CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/11'
# 连接超时
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 180}
# 消息格式
CELERY_ACCEPT_CONNECT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'  # 任务序列化和反序列化使⽤json
CELERY_RESULT_SERIALIZER = 'json'
# 时区
CELERY_TIMEZONE = TIME_ZONE
os.environ.setdefault('C_FORCE_ROOT','True')
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
#verify_code
# 字母验证码
CAPTCHA_IMAGE_SIZE = (100, 50)  # 设置 captcha 图片大小
# CAPTCHA_LENGTH = 4  # 字符个数
CAPTCHA_TIMEOUT = 1  # 超时(minutes)

# 加减乘除验证码
CAPTCHA_OUTPUT_FORMAT = '%(image)s %(text_field)s %(hidden_field)s '
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_null',
                           # 'captcha.helpers.noise_arcs',  # 线
                           'captcha.helpers.noise_dots',  # 点
                           )
# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
OPS_TOKEN = os.environ.get('OPS_TOKEN','kn6xCoKsNkdMvwDOwmyiYgsyL6y7')
ENCRYPT_KEY = os.environ.get('ENCRYPT_KEY','noUjOmvz5zgot45GzQcdFj3258bQs-743hL8HuWEadc=')
ES_HOSTS = os.environ.get("ES_HOSTS", "https://172.30.14.39:9200")
ES_USERNAME = os.environ.get("ES_USERNAME", "elastic")
ES_PWD = os.environ.get("ES_PWD", "123456")
SSO_VALIDATE = os.environ.get("SSO_VALIDATE", "https://xxx")