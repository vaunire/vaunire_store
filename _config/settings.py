import os
from pathlib import Path

# Импорты для удобной работы со статическими файлами и URL
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Импорт функции для загрузки переменных окружения из файла .env
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# BASE_DIR указывает на корень проекта, где лежит manage.py
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ для безопасности проекта
SECRET_KEY = os.getenv('SECRET_KEY')

# Режим отладки: True для разработки, False для продакшена
DEBUG = os.getenv('DEBUG')

# Список разрешённых хостов
ALLOWED_HOSTS = []

# Определение приложений проекта
INSTALLED_APPS = [
    # Приложения из пакета Unfold для улучшенного интерфейса админки
    "unfold", 
    "unfold.contrib.filters", 
    "unfold.contrib.forms", 
    "unfold.contrib.inlines", 
    "unfold.contrib.import_export", 
    "unfold.contrib.guardian",  
    "unfold.contrib.simple_history",

    # Утилита для автоматической перезагрузки браузера в режиме разработки
    'django_browser_reload',
    # Приложение для интеграции Tailwind CSS
    'tailwind', 
    # Приложение для настройки Tailwind CSS
    'tailwind_config', 
    
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_select2',

    # Пользовательские приложения проекта
    'catalog',  # Приложение для музыкального каталога (альбомы, артисты и т.д.)
    'cart',     # Приложение для управления корзиной
    'orders',   # Приложение для заказов
    'profiles', # Приложение для профилей пользователей
]

# Список промежуточных слоёв для обработки запросов
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Корневой файл URL-конфигурации
ROOT_URLCONF = '_config.urls'

# Настройки для Tailwind CSS
TAILWIND_APP_NAME = 'tailwind_config'
INTERNAL_IPS = ["127.0.0.1"]
NPM_BIN_PATH = 'npm.cmd'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates",],
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

# Приложение WSGI для запуска проекта
WSGI_APPLICATION = '_config.wsgi.application'

# Настройки базы данных PostgreSQL, параметры берутся из переменных окружения
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', 5432),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'NAME': os.getenv('POSTGRES_DB', 'postgres'),
        'ATOMIC_REQUEST': True,
    }
}

# Проверяют сложность паролей пользователей
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

# Настройки языка и времени
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')

TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')

USE_I18N = True

USE_TZ = True

# Настройки статических файлов (CSS, JS, изображения)

# Папка для собранных статических файлов (для продакшена)
STATIC_URL = 'static/' 
STATIC_ROOT = BASE_DIR / 'static'

# Дополнительные папки со статическими файлами (для разработки)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_dev'),
]

# Настройки медиафайлов (загружаемые пользователями файлы)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Тип первичного ключа по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
