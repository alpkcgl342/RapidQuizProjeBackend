"""Standart hata zarfı (§7.2).

Tüm 4xx/5xx yanıtları şu yapıdadır:
    {"error": {"code": "...", "message": "...", "details": {...}}}
"""

import logging
from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


class ApiError(exceptions.APIException):
    """Uygulamaya özgü hata. `code` hata zarfındaki makine-okur koddur."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "BAD_REQUEST"
    message = "İstek işlenemedi."

    def __init__(self, message: str | None = None, details: dict[str, Any] | None = None):
        self.message = message or self.message
        self.details = details or {}
        super().__init__(detail=self.message, code=self.code)


class InvalidSessionToken(ApiError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_SESSION_TOKEN"
    message = "Oturum anahtarı eksik veya geçersiz."


class SessionNotOwned(ApiError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "SESSION_NOT_OWNED"
    message = "Bu oturuma erişim yetkin yok."


class NotFound(ApiError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"
    message = "Kayıt bulunamadı."


class AlreadyAnswered(ApiError):
    status_code = status.HTTP_409_CONFLICT
    code = "ALREADY_ANSWERED"
    message = "Bu soru zaten cevaplandı."


class SessionAlreadyFinished(ApiError):
    status_code = status.HTTP_409_CONFLICT
    code = "SESSION_ALREADY_FINISHED"
    message = "Bu oturum zaten bitti."


class SessionNotFinished(ApiError):
    status_code = status.HTTP_409_CONFLICT
    code = "SESSION_NOT_FINISHED"
    message = "Oturum henüz bitmedi."


class ScoreAlreadySubmitted(ApiError):
    status_code = status.HTTP_409_CONFLICT
    code = "SCORE_ALREADY_SUBMITTED"
    message = "Bu oturumun skoru zaten kaydedildi."


class SessionExpired(ApiError):
    status_code = status.HTTP_410_GONE
    code = "SESSION_EXPIRED"
    message = "Oturumun süresi doldu."


class InsufficientQuestions(ApiError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "INSUFFICIENT_QUESTIONS"
    message = "Bu kategori şu an hazırlanıyor."


class UpgradeRequired(ApiError):
    """Desteklenmeyen eski istemci sürümleri için hazır bırakıldı (§11)."""

    status_code = status.HTTP_426_UPGRADE_REQUIRED
    code = "UPGRADE_REQUIRED"
    message = "Uygulamanın yeni sürümüne güncellemen gerekiyor."


def error_body(code: str, message: str, details: Any = None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details or {}}}


_GENERIC: dict[type[exceptions.APIException], tuple[str, str]] = {
    exceptions.ValidationError: ("VALIDATION_ERROR", "Gönderilen veri geçersiz."),
    exceptions.ParseError: ("VALIDATION_ERROR", "İstek gövdesi okunamadı."),
    exceptions.UnsupportedMediaType: ("VALIDATION_ERROR", "Desteklenmeyen içerik türü."),
    exceptions.NotAuthenticated: ("INVALID_SESSION_TOKEN", InvalidSessionToken.message),
    exceptions.AuthenticationFailed: ("INVALID_SESSION_TOKEN", InvalidSessionToken.message),
    exceptions.PermissionDenied: ("PERMISSION_DENIED", "Bu işlem için yetkin yok."),
    exceptions.NotFound: ("NOT_FOUND", NotFound.message),
    exceptions.MethodNotAllowed: ("METHOD_NOT_ALLOWED", "Bu metot desteklenmiyor."),
    exceptions.NotAcceptable: ("NOT_ACCEPTABLE", "İstenen yanıt formatı desteklenmiyor."),
    exceptions.Throttled: ("RATE_LIMITED", "Çok fazla istek gönderdin, biraz bekle."),
}


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)

    if response is None:
        logger.exception("Beklenmeyen hata", exc_info=exc)
        return Response(
            error_body("INTERNAL_ERROR", "Beklenmeyen bir hata oluştu."),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ApiError):
        response.data = error_body(exc.code, exc.message, exc.details)
        return response

    code, message = "ERROR", "İstek işlenemedi."
    for exc_type, (c, m) in _GENERIC.items():
        if isinstance(exc, exc_type):
            code, message = c, m
            break

    details: Any = {}
    if isinstance(exc, exceptions.ValidationError):
        details = exc.detail if isinstance(exc.detail, dict) else {"non_field_errors": exc.detail}
    elif isinstance(exc, exceptions.Throttled) and exc.wait is not None:
        details = {"retry_after_seconds": int(exc.wait)}

    response.data = error_body(code, message, details)
    return response
