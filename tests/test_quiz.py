"""Quiz motoru — §13.1 zorunlu senaryoları dahil."""

import json
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.quiz import services
from apps.quiz.models import QuizSession, QuizSessionQuestion
from tests.factories import make_category_with_questions

pytestmark = pytest.mark.django_db


def _contains_key(obj, key: str) -> bool:
    if isinstance(obj, dict):
        return key in obj or any(_contains_key(v, key) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_key(v, key) for v in obj)
    return False


# --- Puanlama (saf fonksiyonlar) ---


@pytest.mark.parametrize(
    ("elapsed", "points"),
    [(0, 200), (400, 192), (1340, 173), (2500, 150), (4900, 102), (5000, 100), (5700, 100)],
)
def test_compute_points(elapsed, points):
    assert services.compute_points(elapsed) == points


# --- Oturum oluşturma ---


def test_create_session_selects_20_unique_questions(player):
    session = QuizSession.objects.get(pk=player.session_id)
    sqs = list(session.questions.order_by("order"))
    assert len(sqs) == 20
    assert [sq.order for sq in sqs] == list(range(20))
    assert len({sq.question_id for sq in sqs}) == 20
    assert session.client_platform == "web"
    assert session.client_version == "1.0.0"


def test_create_session_response_shape(player):
    body = player.create_response
    assert body["session"]["status"] == "in_progress"
    assert body["session"]["total_questions"] == 20
    assert body["session"]["current_index"] == 0
    assert body["session"]["category"] == {
        "slug": "yazilim",
        "name": "Yazılım",
        "color_hex": "#6C4DFF",
    }
    q = body["question"]
    assert q["index"] == 0
    assert q["time_limit_ms"] == 5000
    assert [o["label"] for o in q["options"]] == ["A", "B", "C", "D"]
    assert q["served_at"].endswith("Z") and q["deadline_at"].endswith("Z")


def test_is_correct_never_leaks_in_question_payloads(player):
    """Soru içeren hiçbir yanıtta `is_correct` / doğru şık bilgisi olmamalı."""
    assert not _contains_key(player.create_response["question"], "is_correct")
    res = player.answer(player.correct_option_id())
    assert not _contains_key(res.json()["next_question"], "is_correct")
    current = player.api.get(f"{player.base}/current-question/", **player.headers()).json()
    assert not _contains_key(current["question"], "is_correct")
    assert "correct" not in json.dumps(current["question"])


def test_unknown_category_404(api, category):
    res = api.post("/api/v1/quiz-sessions/", {"category": "yok"}, format="json")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


def test_insufficient_questions_422(api):
    make_category_with_questions(19, slug="az")
    res = api.post("/api/v1/quiz-sessions/", {"category": "az"}, format="json")
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "INSUFFICIENT_QUESTIONS"


def test_create_session_validation_error(api):
    res = api.post("/api/v1/quiz-sessions/", {}, format="json")
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "category" in res.json()["error"]["details"]


def test_option_order_is_stable_for_same_session(player):
    first = [o["id"] for o in player.question["options"]]
    again = player.api.get(f"{player.base}/current-question/", **player.headers()).json()
    assert [o["id"] for o in again["question"]["options"]] == first


# --- Cevaplama ve süre ---


def test_correct_answer_scores_with_speed_bonus(player):
    player.age_current_question(1000)
    res = player.answer(player.correct_option_id())
    assert res.status_code == 200
    result = res.json()["result"]
    assert result["outcome"] == "correct"
    assert result["is_correct"] is True
    assert result["correct_option_id"] == result["selected_option_id"]
    assert 1000 <= result["elapsed_ms"] < 1500
    assert 170 <= result["points_earned"] <= 180
    session = res.json()["session"]
    assert session["current_index"] == 1
    assert session["correct_count"] == 1
    assert session["score"] == result["points_earned"]
    assert res.json()["next_question"]["index"] == 1


def test_wrong_answer_zero_points_and_reveals_correct(player):
    correct = player.correct_option_id()
    res = player.answer(player.wrong_option_id())
    result = res.json()["result"]
    assert result["outcome"] == "wrong"
    assert result["points_earned"] == 0
    assert result["correct_option_id"] == correct
    assert res.json()["session"]["wrong_count"] == 1


def test_null_selection_is_timeout(player):
    res = player.answer(None)
    assert res.status_code == 200
    assert res.json()["result"]["outcome"] == "timeout"
    assert res.json()["result"]["selected_option_id"] is None
    assert res.json()["session"]["timeout_count"] == 1


def test_answer_at_4900ms_scores(player):
    player.age_current_question(4900)
    result = player.answer(player.correct_option_id()).json()["result"]
    assert result["outcome"] == "correct"
    assert result["points_earned"] >= 100


def test_answer_within_grace_gets_minimum_points(player):
    player.age_current_question(5100)
    result = player.answer(player.correct_option_id()).json()["result"]
    assert result["outcome"] == "correct"
    assert result["points_earned"] == 100


def test_answer_after_grace_is_timeout_with_200(player):
    player.age_current_question(5900)
    res = player.answer(player.correct_option_id())
    assert res.status_code == 200
    assert res.json()["result"]["outcome"] == "timeout"
    assert res.json()["result"]["points_earned"] == 0


def test_second_answer_same_question_409(player):
    qid = player.question["id"]
    first = player.answer(player.correct_option_id(), question_id=qid)
    score = first.json()["session"]["score"]
    second = player.answer(None, question_id=qid)
    assert second.status_code == 409
    err = second.json()["error"]
    assert err["code"] == "ALREADY_ANSWERED"
    assert err["details"]["expected_question_id"] == player.question["id"]
    assert QuizSession.objects.get(pk=player.session_id).score == score


def test_option_from_other_question_400(player):
    first_q_correct = player.correct_option_id()
    player.answer(first_q_correct)
    res = player.answer(first_q_correct)  # önceki sorunun şıkkı
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


# --- current-question ---


def test_current_question_does_not_reset_served_at(player):
    sq = QuizSessionQuestion.objects.get(session_id=player.session_id, order=0)
    player.age_current_question(3000)
    sq.refresh_from_db()
    before = sq.served_at
    res = player.api.get(f"{player.base}/current-question/", **player.headers())
    assert res.status_code == 200
    sq.refresh_from_db()
    assert sq.served_at == before
    assert res.json()["question"]["id"] == player.question["id"]


def test_current_question_times_out_expired_question(player):
    first_id = player.question["id"]
    player.age_current_question(6000)
    res = player.api.get(f"{player.base}/current-question/", **player.headers())
    body = res.json()
    assert body["question"]["index"] == 1
    assert body["question"]["id"] != first_id
    assert body["session"]["timeout_count"] == 1
    sq = QuizSessionQuestion.objects.get(session_id=player.session_id, order=0)
    assert sq.outcome == "timeout"


# --- Oturum sonu ---


def test_full_session_completes_with_summary(player):
    res = player.play_all("correct")
    body = res.json()
    assert body["next_question"] is None
    assert body["session"]["status"] == "completed"
    assert body["session"]["current_index"] == 20
    summary = body["summary"]
    assert summary["correct_count"] == 20
    assert summary["accuracy_pct"] == 100.0
    assert summary["max_possible_score"] == 4000
    assert 3800 <= summary["score"] <= 4000
    assert summary["score_submitted"] is False
    assert summary["estimated_rank"] == 1
    assert summary["average_elapsed_ms"] is not None
    assert summary["finished_at"].endswith("Z")

    again = player.answer(player.correct_option_id())
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "SESSION_ALREADY_FINISHED"

    current = player.api.get(f"{player.base}/current-question/", **player.headers()).json()
    assert current["question"] is None
    assert current["session"]["status"] == "completed"


def test_summary_endpoint_and_elapsed_rules(player):
    player.answer(None)  # timeout → 5000 ms sayılır
    for _ in range(19):
        player.answer(player.wrong_option_id())
    summary = player.api.get(f"{player.base}/summary/", **player.headers()).json()
    assert summary["timeout_count"] == 1
    assert summary["wrong_count"] == 19
    assert summary["fastest_correct_ms"] is None
    assert summary["total_elapsed_ms"] >= 5000
    assert summary["average_elapsed_ms"] < 1000


def test_summary_before_finish_409(player):
    res = player.api.get(f"{player.base}/summary/", **player.headers())
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "SESSION_NOT_FINISHED"


# --- Yetkilendirme ---


def test_missing_token_401(player):
    res = player.api.get(f"{player.base}/current-question/")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_SESSION_TOKEN"


def test_wrong_token_401(player):
    res = player.api.get(f"{player.base}/current-question/", **player.headers("yanlis-token"))
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_SESSION_TOKEN"


def test_other_session_id_403(player, make_player):
    other = make_player("yazilim")
    res = player.api.get(f"{other.base}/current-question/", **player.headers())
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "SESSION_NOT_OWNED"


def test_expired_session_410(player):
    QuizSession.objects.filter(pk=player.session_id).update(
        expires_at=timezone.now() - timedelta(seconds=1)
    )
    res = player.answer(player.correct_option_id())
    assert res.status_code == 410
    assert res.json()["error"]["code"] == "SESSION_EXPIRED"
    assert QuizSession.objects.get(pk=player.session_id).status == "abandoned"
    res = player.api.get(f"{player.base}/current-question/", **player.headers())
    assert res.status_code == 410


# --- Bakım komutu ---


def test_cleanup_stale_sessions(player, make_player):
    fresh = make_player("yazilim")
    QuizSession.objects.filter(pk=player.session_id).update(
        expires_at=timezone.now() - timedelta(minutes=1)
    )
    call_command("cleanup_stale_sessions")
    assert QuizSession.objects.get(pk=player.session_id).status == "abandoned"
    assert QuizSession.objects.get(pk=fresh.session_id).status == "in_progress"
