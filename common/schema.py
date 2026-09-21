"""OpenAPI için ortak hata zarfı şeması (§7.2)."""

from drf_spectacular.utils import OpenApiResponse, inline_serializer
from rest_framework import serializers

ErrorEnvelope = inline_serializer(
    "ErrorEnvelope",
    {
        "error": inline_serializer(
            "ErrorBody",
            {
                "code": serializers.CharField(),
                "message": serializers.CharField(),
                "details": serializers.DictField(),
            },
        )
    },
)

_DESCRIPTIONS = {
    400: "VALIDATION_ERROR",
    401: "INVALID_SESSION_TOKEN",
    403: "SESSION_NOT_OWNED",
    404: "NOT_FOUND",
    409: "ALREADY_ANSWERED / SESSION_ALREADY_FINISHED / SESSION_NOT_FINISHED / "
    "SCORE_ALREADY_SUBMITTED",
    410: "SESSION_EXPIRED",
    422: "INSUFFICIENT_QUESTIONS",
    429: "RATE_LIMITED (Retry-After başlığı döner)",
}


def ERROR_RESPONSES(*codes: int) -> dict[int, OpenApiResponse]:  # noqa: N802
    return {c: OpenApiResponse(ErrorEnvelope, description=_DESCRIPTIONS[c]) for c in codes}
