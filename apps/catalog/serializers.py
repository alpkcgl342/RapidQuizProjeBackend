from django.conf import settings
from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    questions_per_session = serializers.SerializerMethodField()
    available_question_count = serializers.IntegerField(read_only=True)
    is_playable = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "slug",
            "name",
            "description",
            "color_hex",
            "icon",
            "questions_per_session",
            "available_question_count",
            "is_playable",
        ]

    def get_questions_per_session(self, obj) -> int:
        return settings.QUIZ["QUESTIONS_PER_SESSION"]

    def get_is_playable(self, obj) -> bool:
        return obj.available_question_count >= settings.QUIZ["QUESTIONS_PER_SESSION"]


class CategoryListSerializer(serializers.Serializer):
    results = CategorySerializer(many=True)


class CategoryRefSerializer(serializers.ModelSerializer):
    """Diğer yanıtlara gömülen kısa kategori bilgisi."""

    class Meta:
        model = Category
        fields = ["slug", "name", "color_hex"]
