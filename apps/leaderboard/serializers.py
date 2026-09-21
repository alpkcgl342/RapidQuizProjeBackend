from rest_framework import serializers

from apps.catalog.models import Category
from apps.catalog.serializers import CategoryRefSerializer
from common.fields import UtcDateTimeField

from .services import PERIODS


class LeaderboardQuerySerializer(serializers.Serializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.filter(is_active=True), required=False
    )
    limit = serializers.IntegerField(min_value=1, max_value=50, default=10)
    offset = serializers.IntegerField(min_value=0, default=0)
    period = serializers.ChoiceField(choices=PERIODS, default="all")


class CategoryBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["slug", "name", "color_hex"]


class LeaderboardRowSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rank = serializers.IntegerField()
    nickname = serializers.CharField()
    score = serializers.IntegerField()
    correct_count = serializers.IntegerField()
    category = CategoryBadgeSerializer()
    created_at = UtcDateTimeField()


class LeaderboardResponseSerializer(serializers.Serializer):
    scope = serializers.ChoiceField(choices=["category", "overall"])
    category = CategoryRefSerializer(allow_null=True)
    period = serializers.CharField()
    count = serializers.IntegerField()
    results = LeaderboardRowSerializer(many=True)


class EntrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nickname = serializers.CharField()
    score = serializers.IntegerField()
    category = CategoryBadgeSerializer()
    rank_in_category = serializers.IntegerField()
    rank_overall = serializers.IntegerField()
    created_at = UtcDateTimeField()


class SubmitLeaderboardSerializer(serializers.Serializer):
    scope = serializers.CharField()
    category = serializers.CharField()
    top = LeaderboardRowSerializer(many=True)
    user_entry_id = serializers.IntegerField()


class SubmitScoreResponseSerializer(serializers.Serializer):
    entry = EntrySerializer()
    leaderboard = SubmitLeaderboardSerializer()


def rows(entries, start_rank: int = 1) -> list[dict]:
    return [
        {
            "id": e.id,
            "rank": start_rank + i,
            "nickname": e.nickname,
            "score": e.score,
            "correct_count": e.correct_count,
            "category": e.category,
            "created_at": e.created_at,
        }
        for i, e in enumerate(entries)
    ]
