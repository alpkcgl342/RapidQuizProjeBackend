from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient

from apps.catalog.models import AnswerOption
from apps.quiz.models import QuizSessionQuestion
from tests.factories import make_category_with_questions


@pytest.fixture(autouse=True)
def _clear_cache():
    """Throttle sayaçları testler arasında taşınmasın."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def category(db):
    return make_category_with_questions(20, slug="yazilim", name="Yazılım")


class Player:
    """Bir oturumu API üzerinden oynatan test yardımcısı."""

    def __init__(self, api: APIClient, category_slug: str):
        self.api = api
        res = api.post(
            "/api/v1/quiz-sessions/",
            {"category": category_slug},
            format="json",
            HTTP_X_CLIENT_PLATFORM="web",
            HTTP_X_CLIENT_VERSION="1.0.0",
        )
        assert res.status_code == 201, res.content
        self.create_response = res.json()
        self.session_id = self.create_response["session"]["id"]
        self.token = self.create_response["session"]["token"]
        self.question = self.create_response["question"]

    @property
    def base(self) -> str:
        return f"/api/v1/quiz-sessions/{self.session_id}"

    def headers(self, token: str | None = None) -> dict:
        return {"HTTP_X_SESSION_TOKEN": token or self.token}

    def age_current_question(self, ms: int) -> None:
        """Mevcut sorunun servis zamanını `ms` milisaniye geriye çeker."""
        QuizSessionQuestion.objects.filter(
            session_id=self.session_id, order=self.question["index"]
        ).update(served_at=timezone.now() - timedelta(milliseconds=ms))

    def correct_option_id(self) -> int:
        return AnswerOption.objects.get(question_id=self.question["id"], is_correct=True).id

    def wrong_option_id(self) -> int:
        return AnswerOption.objects.filter(question_id=self.question["id"], is_correct=False)[0].id

    def answer(self, option_id, question_id=None, token=None):
        res = self.api.post(
            f"{self.base}/answers/",
            {"question_id": question_id or self.question["id"], "selected_option_id": option_id},
            format="json",
            **self.headers(token),
        )
        if res.status_code == 200 and res.json()["next_question"]:
            self.question = res.json()["next_question"]
        return res

    def play_all(self, choose="correct"):
        res = None
        for _ in range(20):
            option = {"correct": self.correct_option_id, "wrong": self.wrong_option_id}[choose]()
            res = self.answer(option)
            assert res.status_code == 200, res.content
        return res


@pytest.fixture
def player(api, category):
    return Player(api, category.slug)


@pytest.fixture
def make_player(api):
    return lambda slug: Player(api, slug)
