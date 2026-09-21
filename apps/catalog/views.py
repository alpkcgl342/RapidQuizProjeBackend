from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from common.throttles import AnonReadThrottle

from .models import Category
from .serializers import CategoryListSerializer, CategorySerializer


class CategoryListView(APIView):
    throttle_classes = [AnonReadThrottle]

    @extend_schema(summary="Kategori listesi", tags=["catalog"], responses=CategoryListSerializer)
    def get(self, request):
        # GROUP BY'lı sorgularda Meta.ordering uygulanmaz; sıra açıkça verilir.
        categories = (
            Category.objects.filter(is_active=True)
            .annotate(
                available_question_count=Count("questions", filter=Q(questions__is_active=True))
            )
            .order_by("display_order", "id")
        )
        return Response({"results": CategorySerializer(categories, many=True).data})
