from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- 生产环境核心配置 ---
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'k9v2mZp5Lq8XyRn4Ws7Ab3Cd0Ef1GhJkLoIuQP123456789')

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# === ALLOWED_HOSTS ===
allowed_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS')
if allowed_hosts_env:
    ALLOWED_HOSTS = allowed_hosts_env.split(',')
else:
    ALLOWED_HOSTS = ['*']

# === Cloudflare 信任配置 ===
CSRF_TRUSTED_ORIGINS = [
    'https://sgzqsnxzyzst.top',
    'https://www.sgzqsnxzyzst.top',
    'https://sgzqsnxzyzst.xx.kg',
    'https://origin.sgzqsnxzyzst.xx.kg',
    'http://127.0.0.1',
    'http://localhost'
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'volunteer.apps.VolunteerConfig',
    'ckeditor',
    'ckeditor_uploader',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'volunteer.middleware.TimeRestrictionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 60,
        'DISABLE_SERVER_SIDE_CURSORS': True,
        'OPTIONS': {
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'application_name': 'volunteer_platform',
            'cursor_factory': None,
        }
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"
CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'versionCheck': False,
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'login'

# Session配置（记住我功能）
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_NAME = 'volunteer_sessionid'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

JAZZMIN_SETTINGS = {
    "site_title": "志愿者社团管理",
    "site_header": "苏高职青苏暖心志愿者社团",
    "site_brand": "志愿者社团",
    "welcome_sign": "欢迎回来",
    "copyright": "苏高职青苏暖心志愿者社团",
    "topmenu_links": [{"name": "首页", "url": "admin:index", "permissions": ["auth.view_user"]},{"name": "前台网站", "url": "/", "new_window": True}],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {"auth": "fas fa-users-cog","auth.user": "fas fa-user","auth.Group": "fas fa-users","volunteer.Activity": "fas fa-calendar-check","volunteer.Registration": "fas fa-clipboard-list","volunteer.Grade": "fas fa-layer-group","volunteer.VolunteerProfile": "fas fa-address-card"},
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "ui_theme": "lux",
}