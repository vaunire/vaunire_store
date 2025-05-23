import os
from pathlib import Path

# Импорты для удобной работы со статическими файлами и URL
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django.utils.safestring import mark_safe

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

# Получаем ключи Stripe
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Получение API-ключа Яндекс.Карт
YANDEX_MAPS_API_KEY = os.getenv('YANDEX_MAPS_API_KEY')

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

    # Утилита для автоматической перезагрузки браузера в режиме разработки [1]
    'django_browser_reload',
    # Приложение для настройки Tailwind CSS
    'tailwind_config', 'tailwind', 
    # Поддержка улучшенных выпадающих списков
    'django_select2',
    
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'catalog',     # Приложение для музыкального каталога (альбомы, артисты и т.д.)
    'cart',        # Приложение для управления корзиной
    'orders',      # Приложение для заказов
    'accounts',    # Приложение для управления пользователями 
    'promotions',  # Приложение для акций и промокодов
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
    "django_browser_reload.middleware.BrowserReloadMiddleware",  # [2]
]

# Настройки Django Unfold
UNFOLD = {
    "DASHBOARD_CALLBACK": "accounts.views.dashboard_callback",
    "SITE_TITLE": mark_safe(
        """
        <span style="
            font-size: 1.4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        ">VAUNIRE.admin</span>
        <br>
        <span style="
            font-size: 1.1rem;
            color: #1e3a8a;
            font-weight: 400;
        ">Музыкальный интернет – магазин</span>
        """
    ),
    "SITE_HEADER": " ",
    "SITE_ICON": lambda request: static("images/logo/logo_admin.png"),
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "48x48",
            "type": "image/svg+xml",
            "href": lambda request: static("images/logo/favicon.svg"),
        },
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "separator": False,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Информационная панель"),
                        "icon": "monitoring",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Справочники"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Альбомы"),
                        "icon": "album",
                        "link": reverse_lazy("admin:catalog_album_changelist"),
                    },
                    {
                        "title": _("Исполнители"),
                        "icon": "artist",
                        "link": reverse_lazy("admin:catalog_artist_changelist"),
                    },
                    {
                        "title": _("Музыканты"),
                        "icon": "group",
                        "link": reverse_lazy("admin:catalog_member_changelist"),
                    },
                    {
                        "title": _("Жанры"),
                        "icon": "music_note",
                        "link": reverse_lazy("admin:catalog_genre_changelist"),
                    },
                    {
                        "title": _("Стили"),
                        "icon": "queue_music",
                        "link": reverse_lazy("admin:catalog_style_changelist"),
                    },
                    {
                        "title": _("Медианосители"),
                        "icon": "audio_video_receiver",
                        "link": reverse_lazy("admin:catalog_mediatype_changelist"),
                    },
                    {
                        "title": _("Лейблы"),
                        "icon": "instant_mix",
                        "link": reverse_lazy("admin:catalog_label_changelist"),
                    },
                    {
                        "title": _("Страны"),
                        "icon": "flag",
                        "link": reverse_lazy("admin:catalog_country_changelist"),
                    },
                    {
                        "title": _("Галерея изображений"),
                        "icon": "image",
                        "link": reverse_lazy("admin:catalog_imagegallery_changelist"),
                    },
                    {
                        "title": _("Покупатели"),
                        "icon": "groups",
                        "link": reverse_lazy("admin:accounts_customer_changelist"),
                    },
                    {
                        "title": _("Уведомления"),
                        "icon": "notifications_active",
                        "link": reverse_lazy("admin:accounts_notifications_changelist"),
                    },
                ],
            },
            {
                "title": _("Заказы и платежи"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Заказы"),
                        "icon": "shopping_bag",
                        "link": reverse_lazy("admin:orders_order_changelist"),
                    },
                    {
                        "title": _("Платежи"),
                        "icon": "payment",
                        "link": reverse_lazy("admin:orders_payment_changelist"),
                    },
                    {
                        "title": _("Заявки на возврат"),
                        "icon": "assignment_return",
                        "link": reverse_lazy("admin:orders_returnrequest_changelist"),
                    },
                ],
            },
            {
                "title": _("Прайс-листы"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Прайс-листы"),
                        "icon": "currency_ruble",
                        "link": reverse_lazy("admin:catalog_pricelist_changelist"),
                    },
                    {
                        "title": _("Позиции прайс-листа"),
                        "icon": "menu",
                        "link": reverse_lazy("admin:catalog_pricelistitem_changelist"),
                    },
                ],
            },
            {
                "title": _("Корзина"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Корзины"),
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:cart_cart_changelist"),
                    },
                    {
                        "title": _("Продукты корзины"),
                        "icon": "add_shopping_cart",
                        "link": reverse_lazy("admin:cart_cartproduct_changelist"),
                    },
                ],
            },
            {
                "title": _("Акции и промокоды"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Акции"),
                        "icon": "shoppingmode",
                        "link": reverse_lazy("admin:promotions_promotion_changelist"),
                    },
                    {
                        "title": _("Промокоды"),
                        "icon": "checkbook",
                        "link": reverse_lazy("admin:promotions_promocode_changelist"),
                    },
                ],
            },
        ],
    },
    "COLORS": {
        "primary": {
            "50": "239 246 255",    # bg-blue-50
            "100": "219 234 254",   # bg-blue-100
            "200": "191 219 254",   # bg-blue-200
            "300": "147 197 253",   # bg-blue-300
            "400": "96 165 250",    # bg-blue-400
            "500": "59 130 246",    # bg-blue-500 (основной)
            "600": "37 99 235",     # bg-blue-600 
            "700": "29 78 216",     # bg-blue-700
            "800": "30 64 175",     # bg-blue-800
            "900": "30 58 138",     # bg-blue-900
        },
    },
}

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
