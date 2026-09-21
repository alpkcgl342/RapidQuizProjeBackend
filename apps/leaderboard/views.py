from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from common.throttles import AnonReadThrottle

from . import services
from .serializers import LeaderboardQuerySerializer, LeaderboardResponseSerializer, rows


class LeaderboardView(APIView):
    throttle_classes = [AnonReadThrottle]

    @extend_schema(
        summary="Skor tablosu",
        tags=["leaderboard"],
        parameters=[
            OpenApiParameter("category", str, description="Kategori slug'ı; yoksa genel tablo"),
            OpenApiParameter("limit", int, description="1–50, varsayılan 10"),
            OpenApiParameter("offset", int, description="Varsayılan 0"),
            OpenApiParameter("period", str, enum=list(services.PERIODS)),
        ],
        responses=LeaderboardResponseSerializer,
    )
    def get(self, request):
        query = LeaderboardQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        category = query.validated_data.get("category")
        limit = query.validated_data["limit"]
        offset = query.validated_data["offset"]
        period = query.validated_data["period"]

        qs = services.ranked(category, period)
        data = {
            "scope": "category" if category else "overall",
            "category": category,
            "period": period,
            "count": qs.count(),
            "results": rows(qs[offset : offset + limit], start_rank=offset + 1),
        }
        return Response(LeaderboardResponseSerializer(data).data)
