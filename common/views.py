from django.conf import settings
from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from common.fields import iso_utc_ms


class HealthView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    @extend_schema(
        summary="Sağlık kontrolü",
        tags=["health"],
        responses=inline_serializer(
            "Health",
            {
                "status": serializers.CharField(),
                "database": serializers.CharField(),
                "version": serializers.CharField(),
                "time": serializers.DateTimeField(),
            },
        ),
    )
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_ok = True
        except Exception:
            db_ok = False

        return Response(
            {
                "status": "ok" if db_ok else "degraded",
                "database": "ok" if db_ok else "error",
                "version": settings.APP_VERSION,
                "time": iso_utc_ms(timezone.now()),
            },
            status=200 if db_ok else 503,
        )
