"""Quiz girdi/çıktı şemaları. Çıktılar servis katmanının dataclass'larından üretilir;
`is_correct` hiçbir soru çıktısında yer almaz."""

from rest_framework import serializers

from apps.catalog.serializers import CategoryRefSerializer
from common.fields import UtcDateTimeField

# --- Girdi ---


class CreateSessionSerializer(serializers.Serializer):
    category = serializers.SlugField(max_length=50)


class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    selected_option_id = serializers.IntegerField(min_value=1, allow_null=True)


class SubmitScoreSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=100, trim_whitespace=False)


# --- Çıktı ---


class ServedOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField()
    text = serializers.CharField()


class ServedQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    index = serializers.IntegerField()
    text = serializers.CharField()
    options = ServedOptionSerializer(many=True)
    time_limit_ms = serializers.IntegerField()
    served_at = UtcDateTimeField()
    deadline_at = UtcDateTimeField()


class SessionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    token = serializers.CharField()
    category = CategoryRefSerializer()
    total_questions = serializers.IntegerField()
    current_index = serializers.IntegerField()
    score = serializers.IntegerField()
    status = serializers.CharField()
    expires_at = UtcDateTimeField()


class SessionProgressSerializer(serializers.Serializer):
    current_index = serializers.IntegerField()
    score = serializers.IntegerField()
    correct_count = serializers.IntegerField()
    wrong_count = serializers.IntegerField()
    timeout_count = serializers.IntegerField()
    status = serializers.CharField()


class CreateSessionResponseSerializer(serializers.Serializer):
    session = SessionSerializer()
    question = ServedQuestionSerializer()


class CurrentQuestionResponseSerializer(serializers.Serializer):
    question = ServedQuestionSerializer(allow_null=True)
    session = SessionProgressSerializer()


class AnswerResultSerializer(serializers.Serializer):
    outcome = serializers.ChoiceField(choices=["correct", "wrong", "timeout"])
    is_correct = serializers.BooleanField()
    correct_option_id = serializers.IntegerField()
    selected_option_id = serializers.IntegerField(allow_null=True)
    elapsed_ms = serializers.IntegerField()
    points_earned = serializers.IntegerField()
    explanation = serializers.CharField(allow_blank=True)


class SummarySerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    category = CategoryRefSerializer()
    status = serializers.CharField()
    score = serializers.IntegerField()
    max_possible_score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    correct_count = serializers.IntegerField()
    wrong_count = serializers.IntegerField()
    timeout_count = serializers.IntegerField()
    accuracy_pct = serializers.FloatField()
    average_elapsed_ms = serializers.IntegerField(allow_null=True)
    fastest_correct_ms = serializers.IntegerField(allow_null=True)
    total_elapsed_ms = serializers.IntegerField()
    score_submitted = serializers.BooleanField()
    estimated_rank = serializers.IntegerField()
    finished_at = UtcDateTimeField()


class AnswerResponseSerializer(serializers.Serializer):
    result = AnswerResultSerializer()
    session = SessionProgressSerializer()
    next_question = ServedQuestionSerializer(allow_null=True)
    summary = SummarySerializer(required=False, help_text="Yalnızca son soruda bulunur.")
