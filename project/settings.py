from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- 生产环境核心配置 ---
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-key-for-local-dev')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# 允许所有主机头 (因为 Cloudflare 会代理请求)
ALLOWED_HOSTS = ['*']

# === 关键修复：信任你的域名 (解决登录报错 403 Forbidden) ===
CSRF_TRUSTED_ORIGINS = [
    'https://sgzqsnxzyzst.top',
    'https://www.sgzqsnxzyzst.top',
    # 如果你还用那个 .kg 域名，也加进去
    'https://sgzqsnxzyzst.xx.kg',
    'http://127.0.0.1',
    'http://localhost'
]

# === 关键修复：告诉 Django 它是运行在 HTTPS 代理后面的 ===
# 没有这一行，Django 会以为连接是不安全的，从而拒绝 CSRF Cookie
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# -----------------------

# 详细日志配置
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
    'axes',
    'ckeditor',
    'ckeditor_uploader',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
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

# 数据库配置
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
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# 媒体文件配置 (Logo 和上传图片)
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
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.1
AXES_LOCKOUT_TEMPLATE = 'volunteer/lockout.html'
LOGIN_URL = 'login'

JAZZMIN_SETTINGS = {
    "site_title": "志愿者社团管理",
    "site_header": "苏高职“青苏”暖心志愿者社团",
    "site_brand": "志愿者社团",
    "welcome_sign": "欢迎回来",
    "copyright": "苏高职“青苏”暖心志愿者社团",
    "topmenu_links": [{"name": "首页", "url": "admin:index", "permissions": ["auth.view_user"]},{"name": "前台网站", "url": "/", "new_window": True}],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {"auth": "fas fa-users-cog","auth.user": "fas fa-user","auth.Group": "fas fa-users","volunteer.Activity": "fas fa-calendar-check","volunteer.Registration": "fas fa-clipboard-list","volunteer.Grade": "fas fa-layer-group","volunteer.VolunteerProfile": "fas fa-address-card"},
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "ui_theme": "lux",
}