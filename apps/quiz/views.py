from dataclasses import asdict

from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.leaderboard import services as leaderboard
from apps.leaderboard.serializers import SubmitScoreResponseSerializer, rows
from common.nickname import validate_nickname
from common.schema import ERROR_RESPONSES
from common.throttles import AnswerThrottle, ScoreSubmitThrottle, SessionCreateThrottle

from . import services
from .authentication import IsSessionOwner, SessionTokenAuthentication
from .serializers import (
    AnswerResponseSerializer,
    AnswerSerializer,
    CreateSessionResponseSerializer,
    CreateSessionSerializer,
    CurrentQuestionResponseSerializer,
    ServedQuestionSerializer,
    SessionProgressSerializer,
    SessionSerializer,
    SubmitScoreSerializer,
    SummarySerializer,
)

CLIENT_HEADERS = [
    OpenApiParameter(
        "X-Client-Platform", str, OpenApiParameter.HEADER, enum=["web", "ios", "android"]
    ),
    OpenApiParameter("X-Client-Version", str, OpenApiParameter.HEADER),
]


def _question(served):
    return ServedQuestionSerializer(served).data if served else None


class QuizSessionCreateView(APIView):
    throttle_classes = [SessionCreateThrottle]

    @extend_schema(
        summary="Oturum başlat ve ilk soruyu al",
        tags=["quiz"],
        parameters=CLIENT_HEADERS,
        request=CreateSessionSerializer,
        responses={201: CreateSessionResponseSerializer, **ERROR_RESPONSES(400, 404, 422, 429)},
    )
    def post(self, request):
        body = CreateSessionSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        session, served = services.create_session(
            body.validated_data["category"],
            client_platform=request.headers.get("X-Client-Platform", ""),
            client_version=request.headers.get("X-Client-Version", ""),
        )
        return Response(
            {"session": SessionSerializer(session).data, "question": _question(served)},
            status=status.HTTP_201_CREATED,
        )


class SessionScopedView(APIView):
    authentication_classes = [SessionTokenAuthentication]
    permission_classes = [IsSessionOwner]

    @property
    def quiz_session(self):
        return self.request.auth


SESSION_ID = OpenApiParameter("id", str, OpenApiParameter.PATH, description="Oturum UUID'si")


class CurrentQuestionView(SessionScopedView):
    @extend_schema(
        summary="Sıradaki soruyu al (kaldığı yerden devam)",
        tags=["quiz"],
        parameters=[SESSION_ID],
        responses={200: CurrentQuestionResponseSerializer, **ERROR_RESPONSES(401, 403, 410)},
    )
    def get(self, request, pk):
        session, served = services.get_current_question(self.quiz_session)
        return Response(
            {"question": _question(served), "session": SessionProgressSerializer(session).data}
        )


class AnswerView(SessionScopedView):
    throttle_classes = [AnswerThrottle]

    @extend_schema(
        summary="Sıradaki soruya cevap gönder",
        description=(
            "`selected_option_id: null` cevapsız (timeout) demektir. Süre aşımı hata değil, "
            '`200` + `outcome: "timeout"` olarak döner. Son soruda `next_question` null olur '
            "ve `summary` eklenir."
        ),
        tags=["quiz"],
        parameters=[SESSION_ID],
        request=AnswerSerializer,
        responses={200: AnswerResponseSerializer, **ERROR_RESPONSES(400, 401, 403, 409, 410, 429)},
    )
    def post(self, request, pk):
        body = AnswerSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        outcome = services.submit_answer(
            self.quiz_session,
            question_id=body.validated_data["question_id"],
            selected_option_id=body.validated_data["selected_option_id"],
        )
        data = {
            "result": asdict(outcome.result),
            "session": SessionProgressSerializer(outcome.session).data,
            "next_question": _question(outcome.next_question),
        }
        if outcome.next_question is None:
            data["summary"] = SummarySerializer(services.build_summary(outcome.session)).data
        return Response(data)


class SummaryView(SessionScopedView):
    @extend_schema(
        summary="Biten oturumun özeti",
        tags=["quiz"],
        parameters=[SESSION_ID],
        responses={200: SummarySerializer, **ERROR_RESPONSES(401, 403, 409)},
    )
    def get(self, request, pk):
        return Response(SummarySerializer(services.build_summary(self.quiz_session)).data)


class SubmitScoreView(SessionScopedView):
    throttle_classes = [ScoreSubmitThrottle]

    @extend_schema(
        summary="Skoru takma adla skor tablosuna kaydet",
        tags=["quiz", "leaderboard"],
        parameters=[SESSION_ID],
        request=SubmitScoreSerializer,
        responses={
            201: SubmitScoreResponseSerializer,
            **ERROR_RESPONSES(400, 401, 403, 409, 410, 429),
        },
    )
    def post(self, request, pk):
        body = SubmitScoreSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            nickname = validate_nickname(body.validated_data["nickname"])
        except DjangoValidationError as exc:
            raise ValidationError({"nickname": exc.messages}) from exc

        result = leaderboard.submit_score(self.quiz_session, nickname)
        entry = result.entry
        data = {
            "entry": {
                "id": entry.id,
                "nickname": entry.nickname,
                "score": entry.score,
                "category": entry.category,
                "rank_in_category": result.rank_in_category,
                "rank_overall": result.rank_overall,
                "created_at": entry.created_at,
            },
            "leaderboard": {
                "scope": "category",
                "category": entry.category.slug,
                "top": rows(result.top),
                "user_entry_id": entry.id,
            },
        }
        return Response(SubmitScoreResponseSerializer(data).data, status=status.HTTP_201_CREATED)
