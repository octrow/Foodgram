import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", False) == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "djoser",
    "colorfield",
    "users.apps.UsersConfig",
    "recipes.apps.RecipesConfig",
    "api.apps.ApiConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "foodgram.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3"
        if os.getenv("USE_SQLITE")
        else "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "django"),
        "USER": os.getenv("POSTGRES_USER", "django"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", 5432),
    }
}

AUTH_USER_MODEL = "users.User"

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

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 6,
    "PAGINATE_BY_PARAM": "limit",
}

DJOSER = {
    "SERIALIZERS": {
        "user": "api.serializers.UserSerializer",
        "current_user": "api.serializers.UserSerializer",
    },
    "PERMISSIONS": {
        "user": ["djoser.permissions.CurrentUserOrAdminOrReadOnly"],
        "user_list": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    },
    "HIDE_USERS": False,
    "LOGIN_FIELD": "email",
}

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CONSTANTS

MAX_LEN_EMAIL = 254
MAX_LEN_NAME = 150
MAX_LEN_TITLE = 200
MIN_VALUE = 1
MAX_VALUE = 32767
MAX_HEX = 7

# users/models
CUSTOM_USER_EMAIL_HELP_TEXT = "Введите вашу электронную почту"
CUSTOM_USER_FIRST_NAME_HELP_TEXT = "Введите ваше имя"
CUSTOM_USER_LAST_NAME_HELP_TEXT = "Введите вашу фамилию"
CUSTOM_USER_USERNAME_HELP_TEXT = "Введите уникальное имя пользователя"
CUSTOM_USER_IS_ACTIVE_HELP_TEXT = "Отметьте, если пользователь активирован"
SUBSCRIPTION_DATE_ADDED_HELP_TEXT = (
    "Дата, когда пользователь подписался на автора"
)
# recipes/models
INGREDIENT_NAME_HELP_TEXT = "Введите название ингредиента"
INGREDIENT_MEASUREMENT_UNIT_HELP_TEXT = "Введите единицу измерения ингредиента"
TAG_NAME_HELP_TEXT = "Введите название тега"
TAG_COLOR_HELP_TEXT = "Введите HEX-код цвета тега"
TAG_SLUG_HELP_TEXT = "Введите уникальный идентификатор тега"
RECIPE_NAME_HELP_TEXT = "Введите название рецепта"
RECIPE_AUTHOR_HELP_TEXT = "Выберите автора рецепта"
RECIPE_IMAGE_HELP_TEXT = "Загрузите изображение рецепта"
RECIPE_TEXT_HELP_TEXT = "Введите описание рецепта"
RECIPE_COOKING_TIME_HELP_TEXT = "Введите время приготовления рецепта в минутах"
RECIPE_TAGS_HELP_TEXT = "Выберите теги для рецепта"
RECIPE_INGREDIENTS_HELP_TEXT = (
    "Выберите ингредиенты для рецепта и укажите их количество"
)
AMOUNT_INGREDIENT_RECIPE_HELP_TEXT = (
    "Выберите рецепт, к которому относится ингредиент"
)
AMOUNT_INGREDIENT_INGREDIENT_HELP_TEXT = (
    "Выберите ингредиент, который используется в рецепте"
)
AMOUNT_INGREDIENT_AMOUNT_HELP_TEXT = (
    "Введите количество ингредиента в единицах измерения"
)
FAVORITE_USER_HELP_TEXT = (
    "Выберите пользователя, который добавил рецепт в избранное"
)
FAVORITE_RECIPE_HELP_TEXT = "Выберите рецепт, который был добавлен в избранное"
FAVORITE_DATE_ADDED_HELP_TEXT = (
    "Дата, когда пользователь добавил рецепт в избранное"
)
SHOPPING_CART_USER_HELP_TEXT = (
    "Выберите пользователя, который добавил рецепт в корзину"
)
SHOPPING_CART_RECIPE_HELP_TEXT = (
    "Выберите рецепт, который был добавлен в корзину"
)
