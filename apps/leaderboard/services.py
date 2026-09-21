from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.catalog.models import Category
from apps.quiz.models import QuizSession
from apps.quiz.services import session_elapsed_stats
from common.exceptions import ScoreAlreadySubmitted, SessionExpired, SessionNotFinished

from .models import RANK_ORDERING, LeaderboardEntry

PERIODS = ("all", "month", "week", "today")


def ranked(
    category: Category | None = None, period: str = "all", now: datetime | None = None
) -> QuerySet[LeaderboardEntry]:
    qs = LeaderboardEntry.objects.select_related("category").order_by(*RANK_ORDERING)
    if category is not None:
        qs = qs.filter(category=category)
    since = period_start(period, now)
    if since is not None:
        qs = qs.filter(created_at__gte=since)
    return qs


def period_start(period: str, now: datetime | None = None) -> datetime | None:
    now = now or timezone.now()
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "week":
        return now - timedelta(days=7)
    if period == "month":
        return now - timedelta(days=30)
    return None


def _scope(category: Category | None) -> QuerySet[LeaderboardEntry]:
    qs = LeaderboardEntry.objects.all()
    return qs.filter(category=category) if category is not None else qs


def rank_of_entry(entry: LeaderboardEntry, category: Category | None = None) -> int:
    """Kaydın sırası (1-tabanlı). `category` None ise genel sıralama."""
    ahead = _scope(category).filter(
        Q(score__gt=entry.score)
        | Q(score=entry.score, total_elapsed_ms__lt=entry.total_elapsed_ms)
        | Q(
            score=entry.score,
            total_elapsed_ms=entry.total_elapsed_ms,
            created_at__lt=entry.created_at,
        )
        | Q(
            score=entry.score,
            total_elapsed_ms=entry.total_elapsed_ms,
            created_at=entry.created_at,
            id__lt=entry.id,
        )
    )
    return ahead.count() + 1


def estimated_rank(category: Category, score: int, total_elapsed_ms: int) -> int:
    """Skor şimdi kaydedilse kategoride kaçıncı olurdu (eşitlerde önce kaydeden üstte)."""
    ahead = _scope(category).filter(
        Q(score__gt=score) | Q(score=score, total_elapsed_ms__lte=total_elapsed_ms)
    )
    return ahead.count() + 1


@dataclass(frozen=True)
class SubmitResult:
    entry: LeaderboardEntry
    rank_in_category: int
    rank_overall: int
    top: list[LeaderboardEntry]


def submit_score(session: QuizSession, nickname: str) -> SubmitResult:
    """Biten oturumun skorunu bir kez kaydeder (§7.8). Puan istemciden değil oturumdan gelir."""
    with transaction.atomic():
        session = (
            QuizSession.objects.select_for_update().select_related("category").get(pk=session.pk)
        )
        if session.status == QuizSession.Status.ABANDONED:
            raise SessionExpired()
        if session.status != QuizSession.Status.COMPLETED:
            raise SessionNotFinished()
        if LeaderboardEntry.objects.filter(session=session).exists():
            raise ScoreAlreadySubmitted()
        try:
            entry = LeaderboardEntry.objects.create(
                session=session,
                category=session.category,
                nickname=nickname,
                score=session.score,
                correct_count=session.correct_count,
                total_elapsed_ms=session_elapsed_stats(session)["total_elapsed_ms"],
            )
        except IntegrityError:
            raise ScoreAlreadySubmitted() from None

    top_n = settings.LEADERBOARD_TOP_N
    return SubmitResult(
        entry=entry,
        rank_in_category=rank_of_entry(entry, category=session.category),
        rank_overall=rank_of_entry(entry),
        top=list(ranked(session.category)[:top_n]),
    )
