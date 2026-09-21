"""Production ayarları (§14.4).

Docker build sırasında `collectstatic` sahte SECRET_KEY / DATABASE_URL ile bu modülü
import eder; bu yüzden build anında zorunlu olmayan her şeyin varsayılanı olmalıdır.
"""

from .base import *  # noqa: F403
from .base import DATABASES, env

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])  # yalnızca admin için

# App Platform TLS'i kendi katmanında sonlandırıp X-Forwarded-Proto gönderir.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
# Health check platformun iç ağından HTTP ile gelir; yönlendirilmemeli.
SECURE_REDIRECT_EXEMPT = [r"^api/v1/health/$"]
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"].setdefault("OPTIONS", {})["sslmode"] = env("DB_SSLMODE", default="require")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# DO App Platform gerçek istemci IP'sini DO-Connecting-IP başlığında iletir.
IPWARE_META_PRECEDENCE_ORDER = tuple(
    env.list(
        "IPWARE_META_PRECEDENCE_ORDER",
        default=["HTTP_DO_CONNECTING_IP", "HTTP_X_FORWARDED_FOR", "REMOTE_ADDR"],
    )
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": (
                '{"time": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            )
        },
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
