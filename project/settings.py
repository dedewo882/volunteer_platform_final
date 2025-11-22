from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- 生产环境核心配置 ---
# 使用之前生成的强密钥 (不含特殊字符，防止 Docker 误判)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'k9v2mZp5Lq8XyRn4Ws7Ab3Cd0Ef1GhJkLoIuQP123456789')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# 允许所有主机头 (适配 Cloudflare)
ALLOWED_HOSTS = ['*']

# === Cloudflare 信任配置 (防止 CSRF 报错) ===
CSRF_TRUSTED_ORIGINS = [
    'https://sgzqsnxzyzst.top',
    'https://www.sgzqsnxzyzst.top',
    'https://sgzqsnxzyzst.xx.kg',
    'http://127.0.0.1',
    'http://localhost'
]
# 告诉 Django它是运行在 HTTPS 代理后面的
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

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
    # 'axes',  <-- [已删除] 彻底移除防爆破插件，防止误封
    'ckeditor',
    'ckeditor_uploader',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # === [核心省钱策略] ===
    # 必须放在 SessionMiddleware 之前！
    # 这样在深夜访问时，请求会被直接拦截，不会去连接数据库查 Session。
    'volunteer.middleware.TimeRestrictionMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware', # <--- 这个会连接数据库
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'axes.middleware.AxesMiddleware', <-- [已删除]
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
        'CONN_MAX_AGE': 60, # 保持连接 60秒
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
    # 'axes.backends.AxesBackend', <-- [已删除]
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]
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

# 后台 UI 配置 (Jazzmin)
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