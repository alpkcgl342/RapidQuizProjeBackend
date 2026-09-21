"""Tüm ortamlarda ortak Django ayarları. Değerler .env / ortam değişkenlerinden okunur."""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

APP_VERSION = "1.0.0"

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3. parti
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    # proje
    "apps.catalog",
    "apps.quiz",
    "apps.leaderboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=0)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "tr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- Cache: REDIS_URL varsa Redis, yoksa LocMem (§14.7) ---
REDIS_URL = env("REDIS_URL", default="")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "common.exceptions.api_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "session_create": env("THROTTLE_SESSION_CREATE", default="30/hour"),
        "answer": env("THROTTLE_ANSWER", default="600/hour"),
        "score_submit": env("THROTTLE_SCORE_SUBMIT", default="20/hour"),
        "anon_read": env("THROTTLE_ANON_READ", default="300/hour"),
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Rapid Quiz API",
    "DESCRIPTION": (
        "Kayıt gerektirmeyen, soru başına 5 saniyelik hızlı quiz uygulamasının REST API'si. "
        "Aktif oturum işlemleri `X-Session-Token` başlığıyla yetkilendirilir."
    ),
    "VERSION": APP_VERSION,
    "SERVE_INCLUDE_SCHEMA": False,
    "OAS_VERSION": "3.1.0",
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]+",
}

# --- CORS (§8.6) ---
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-language",
    "content-type",
    "x-session-token",
    "x-client-platform",
    "x-client-version",
]
CORS_ALLOW_CREDENTIALS = False
CORS_URLS_REGEX = r"^/api/.*$"

# --- İstemci IP'si (throttling için, §14.4) ---
# Sıra önemli: listede ilk bulunan başlık kullanılır. DO App Platform gerçek istemci
# IP'sini DO-Connecting-IP başlığında iletir; yerelde REMOTE_ADDR yeterlidir.
IPWARE_META_PRECEDENCE_ORDER = tuple(
    env.list("IPWARE_META_PRECEDENCE_ORDER", default=["REMOTE_ADDR"])
)

# --- Oyun parametreleri (§8.8) — sabit kodlanmaz ---
QUIZ = {
    "QUESTIONS_PER_SESSION": env.int("QUIZ_QUESTIONS_PER_SESSION", default=20),
    "TIME_LIMIT_MS": env.int("QUIZ_TIME_LIMIT_MS", default=5000),
    "GRACE_PERIOD_MS": env.int("QUIZ_GRACE_PERIOD_MS", default=800),
    # Cevap sonrası geri bildirim süresi; sonraki sorunun served_at'i bu kadar ileri alınır.
    "FEEDBACK_DELAY_MS": env.int("QUIZ_FEEDBACK_DELAY_MS", default=1200),
    "SESSION_TTL_MINUTES": env.int("QUIZ_SESSION_TTL_MINUTES", default=30),
    "BASE_POINTS": env.int("QUIZ_BASE_POINTS", default=100),
    "MAX_SPEED_BONUS": env.int("QUIZ_MAX_SPEED_BONUS", default=100),
}
LEADERBOARD_TOP_N = env.int("LEADERBOARD_TOP_N", default=10)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
