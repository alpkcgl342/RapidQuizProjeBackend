import pytest

from apps.leaderboard.models import LeaderboardEntry
from apps.quiz.models import QuizSession
from tests.factories import make_category_with_questions

pytestmark = pytest.mark.django_db


def _submit(player, nickname="hizlisimsek", **extra):
    return player.api.post(
        f"{player.base}/submit-score/",
        {"nickname": nickname, **extra},
        format="json",
        **player.headers(),
    )


def test_submit_score_happy_path(player):
    player.play_all("correct")
    res = _submit(player, "  hızlı   şimşek ")
    assert res.status_code == 201
    body = res.json()
    session = QuizSession.objects.get(pk=player.session_id)
    assert body["entry"]["nickname"] == "hızlı şimşek"
    assert body["entry"]["score"] == session.score
    assert body["entry"]["rank_in_category"] == 1
    assert body["entry"]["rank_overall"] == 1
    assert body["leaderboard"]["user_entry_id"] == body["entry"]["id"]
    assert body["leaderboard"]["top"][0]["id"] == body["entry"]["id"]
    assert body["leaderboard"]["top"][0]["rank"] == 1

    summary = player.api.get(f"{player.base}/summary/", **player.headers()).json()
    assert summary["score_submitted"] is True


def test_submit_score_twice_409(player):
    player.play_all("correct")
    assert _submit(player).status_code == 201
    res = _submit(player, "baska")
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "SCORE_ALREADY_SUBMITTED"
    assert LeaderboardEntry.objects.count() == 1


def test_submit_before_finish_409(player):
    res = _submit(player)
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "SESSION_NOT_FINISHED"


def test_score_comes_from_server_not_client(player):
    player.play_all("wrong")
    res = _submit(player, score=4000)
    assert res.status_code == 201
    assert res.json()["entry"]["score"] == 0
    assert LeaderboardEntry.objects.get().score == 0


def test_invalid_nickname_400(player):
    player.play_all("correct")
    res = _submit(player, "x")
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "nickname" in res.json()["error"]["details"]


def _entry(session, **kw):
    defaults = {"nickname": "n", "score": 100, "correct_count": 1, "total_elapsed_ms": 50000}
    defaults.update(kw)
    return LeaderboardEntry.objects.create(session=session, category=session.category, **defaults)


def _finished_session(category):
    from django.utils import timezone

    return QuizSession.objects.create(
        category=category, status="completed", expires_at=timezone.now()
    )


def test_ordering_ties_broken_by_elapsed_then_created(api, category):
    slow = _entry(_finished_session(category), nickname="yavas", score=3000, total_elapsed_ms=60000)
    fast = _entry(_finished_session(category), nickname="hizli", score=3000, total_elapsed_ms=30000)
    top = _entry(_finished_session(category), nickname="lider", score=3500, total_elapsed_ms=90000)
    twin = _entry(_finished_session(category), nickname="ikiz", score=3000, total_elapsed_ms=30000)

    res = api.get("/api/v1/leaderboard/", {"category": "yazilim"})
    assert res.status_code == 200
    body = res.json()
    assert body["scope"] == "category"
    assert body["count"] == 4
    assert [r["nickname"] for r in body["results"]] == ["lider", "hizli", "ikiz", "yavas"]
    assert [r["rank"] for r in body["results"]] == [1, 2, 3, 4]
    assert {top.id, fast.id, twin.id, slow.id} == {r["id"] for r in body["results"]}


def test_overall_leaderboard_and_pagination(api, category):
    other = make_category_with_questions(0, slug="fizik", name="Fizik")
    for i in range(12):
        _entry(_finished_session(category if i % 2 else other), nickname=f"p{i}", score=i * 100)

    body = api.get("/api/v1/leaderboard/").json()
    assert body["scope"] == "overall"
    assert body["category"] is None
    assert body["count"] == 12
    assert len(body["results"]) == 10
    assert body["results"][0]["nickname"] == "p11"
    assert {r["category"]["slug"] for r in body["results"]} == {"yazilim", "fizik"}

    page2 = api.get("/api/v1/leaderboard/", {"limit": 5, "offset": 10}).json()
    assert [r["rank"] for r in page2["results"]] == [11, 12]


def test_leaderboard_unknown_category_400(api, category):
    res = api.get("/api/v1/leaderboard/", {"category": "yok"})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


def test_estimated_rank(player, category):
    for score in (4000, 3999):
        _entry(_finished_session(category), score=score)
    summary = player.play_all("wrong").json()["summary"]
    assert summary["score"] == 0
    assert summary["estimated_rank"] == 3
