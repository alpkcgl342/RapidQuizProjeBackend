"""Quiz iş mantığı: oturum oluşturma, soru servisi, süre kontrolü, puanlama (§4, §8.1).

HTTP bilmez; view'lar bu fonksiyonları çağırır. Zaman parametresi (`now`) test
edilebilirlik için dışarıdan verilebilir.
"""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.catalog.models import AnswerOption, Category, Question
from common.exceptions import (
    AlreadyAnswered,
    InsufficientQuestions,
    NotFound,
    SessionAlreadyFinished,
    SessionExpired,
    SessionNotFinished,
)

from .models import QuizSession, QuizSessionQuestion

Outcome = QuizSessionQuestion.Outcome
Status = QuizSession.Status
OPTION_LABELS = "ABCD"


def _cfg(key: str) -> int:
    return settings.QUIZ[key]


# ---------------------------------------------------------------------------
# Saf hesaplamalar
# ---------------------------------------------------------------------------


def clamp_elapsed(elapsed_ms: int) -> int:
    return max(0, min(elapsed_ms, _cfg("TIME_LIMIT_MS")))


def compute_points(elapsed_ms: int) -> int:
    """Doğru cevap puanı: taban + doğrusal hız bonusu (§4.2). Yarımlar yukarı yuvarlanır."""
    limit = _cfg("TIME_LIMIT_MS")
    remaining = limit - clamp_elapsed(elapsed_ms)
    bonus = (_cfg("MAX_SPEED_BONUS") * remaining * 2 + limit) // (2 * limit)
    return _cfg("BASE_POINTS") + bonus


def acceptance_window_ms() -> int:
    """Cevabın değerlendirileceği azami süre: limit + grace period."""
    return _cfg("TIME_LIMIT_MS") + _cfg("GRACE_PERIOD_MS")


def elapsed_ms_between(start: datetime, end: datetime) -> int:
    return max(0, int((end - start).total_seconds() * 1000))


# ---------------------------------------------------------------------------
# Dönüş tipleri
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ServedOption:
    id: int
    label: str
    text: str


@dataclass(frozen=True)
class ServedQuestion:
    id: int
    index: int
    text: str
    options: list[ServedOption]
    time_limit_ms: int
    served_at: datetime
    deadline_at: datetime


@dataclass(frozen=True)
class AnswerResult:
    outcome: str
    is_correct: bool
    correct_option_id: int
    selected_option_id: int | None
    elapsed_ms: int
    points_earned: int
    explanation: str


@dataclass(frozen=True)
class AnswerOutcome:
    session: QuizSession
    result: AnswerResult
    next_question: ServedQuestion | None


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------


def _build_served_question(sq: QuizSessionQuestion) -> ServedQuestion:
    """Soruyu istemciye gidecek hale getirir. `is_correct` asla dahil edilmez.

    Şık sırası oturum+soru ikilisine göre deterministik karıştırılır: yenilemede
    aynı sıra döner, ama farklı oturumlarda "doğru hep B" örüntüsü oluşmaz.
    """
    options = list(sq.question.options.all())
    random.Random(f"{sq.session_id}:{sq.question_id}").shuffle(options)
    limit = _cfg("TIME_LIMIT_MS")
    return ServedQuestion(
        id=sq.question_id,
        index=sq.order,
        text=sq.question.text,
        options=[
            ServedOption(id=o.id, label=OPTION_LABELS[i], text=o.text)
            for i, o in enumerate(options)
        ],
        time_limit_ms=limit,
        served_at=sq.served_at,
        deadline_at=sq.served_at + timedelta(milliseconds=limit),
    )


def _current_sq(session: QuizSession) -> QuizSessionQuestion:
    return (
        QuizSessionQuestion.objects.select_related("question")
        .prefetch_related("question__options")
        .get(session=session, order=session.current_index)
    )


def _serve(sq: QuizSessionQuestion, now: datetime) -> ServedQuestion:
    """Soruyu servis eder. `served_at` yalnızca ilk serviste yazılır; yenileme süreyi sıfırlamaz."""
    if sq.served_at is None:
        sq.served_at = now
        sq.save(update_fields=["served_at"])
        Question.objects.filter(pk=sq.question_id).update(times_served=F("times_served") + 1)
    return _build_served_question(sq)


def _record_timeout(session: QuizSession, sq: QuizSessionQuestion, now: datetime) -> None:
    sq.outcome = Outcome.TIMEOUT
    sq.is_correct = False
    sq.points = 0
    sq.answered_at = now
    if sq.served_at is not None:
        sq.elapsed_ms = elapsed_ms_between(sq.served_at, now)
    sq.save(update_fields=["outcome", "is_correct", "points", "answered_at", "elapsed_ms"])
    session.timeout_count += 1


def _is_expired(session: QuizSession, now: datetime) -> bool:
    return session.status == Status.IN_PROGRESS and now >= session.expires_at


def _abandon(session: QuizSession) -> None:
    session.status = Status.ABANDONED
    session.save(update_fields=["status"])


def _finalize(session: QuizSession, now: datetime) -> None:
    """Oturumu kapatır: kalan cevapsız sorular `timeout`, durum `completed`."""
    pending = session.questions.filter(outcome=Outcome.PENDING)
    for sq in pending:
        _record_timeout(session, sq, now)
    session.current_index = session.total_questions
    session.status = Status.COMPLETED
    session.finished_at = now
    session.save()


def _lock_session(session_id) -> QuizSession:
    return QuizSession.objects.select_for_update().select_related("category").get(pk=session_id)


# ---------------------------------------------------------------------------
# Genel API
# ---------------------------------------------------------------------------


def create_session(
    category_slug: str,
    client_platform: str = "",
    client_version: str = "",
    now: datetime | None = None,
) -> tuple[QuizSession, ServedQuestion]:
    """Rastgele N soruyla oturum açar ve ilk soruyu servis eder (§4.3)."""
    now = now or timezone.now()
    try:
        category = Category.objects.get(slug=category_slug, is_active=True)
    except Category.DoesNotExist:
        raise NotFound("Kategori bulunamadı.", {"category": category_slug}) from None

    count = _cfg("QUESTIONS_PER_SESSION")
    pool = list(
        Question.objects.filter(category=category, is_active=True).values_list("id", flat=True)
    )
    if len(pool) < count:
        raise InsufficientQuestions(
            details={"category": category.slug, "available": len(pool), "required": count}
        )
    chosen = random.sample(pool, count)

    platform = client_platform if client_platform in QuizSession.Platform.values else ""
    with transaction.atomic():
        session = QuizSession.objects.create(
            category=category,
            total_questions=count,
            client_platform=platform,
            client_version=client_version[:20],
            expires_at=now + timedelta(minutes=_cfg("SESSION_TTL_MINUTES")),
        )
        QuizSessionQuestion.objects.bulk_create(
            QuizSessionQuestion(session=session, question_id=qid, order=i)
            for i, qid in enumerate(chosen)
        )
        served = _serve(_current_sq(session), now)
    return session, served


def get_current_question(
    session: QuizSession, now: datetime | None = None
) -> tuple[QuizSession, ServedQuestion | None]:
    """Sıradaki soruyu döner (§7.5).

    Süresi (limit + grace) geçmiş sorular `timeout` olarak kapatılır ve ilerlenir.
    Oturum bittiyse soru `None` döner.
    """
    now = now or timezone.now()
    served = None
    with transaction.atomic():
        session = _lock_session(session.pk)
        if _is_expired(session, now):
            _abandon(session)
        elif session.status == Status.IN_PROGRESS:
            served = _advance_to_servable(session, now)
    if session.status == Status.ABANDONED:
        raise SessionExpired()
    return session, served


def _advance_to_servable(session: QuizSession, now: datetime) -> ServedQuestion | None:
    window = timedelta(milliseconds=acceptance_window_ms())
    while session.current_index < session.total_questions:
        sq = _current_sq(session)
        if sq.served_at is not None and now > sq.served_at + window:
            _record_timeout(session, sq, now)
            session.current_index += 1
            continue
        session.save(update_fields=["current_index", "timeout_count"])
        return _serve(sq, now)
    _finalize(session, now)
    return None


def submit_answer(
    session: QuizSession,
    question_id: int,
    selected_option_id: int | None,
    now: datetime | None = None,
) -> AnswerOutcome:
    """Sıradaki soruya cevabı işler, puanlar ve sonraki soruyu servis eder (§7.6).

    Oturum satırı `select_for_update` ile kilitlenir; aynı anda gelen iki cevaptan
    yalnızca biri işlenir, diğeri `ALREADY_ANSWERED` alır.
    """
    now = now or timezone.now()
    with transaction.atomic():
        session = _lock_session(session.pk)
        if not _is_expired(session, now):
            return _submit_locked(session, question_id, selected_option_id, now)
        _abandon(session)
    raise SessionExpired()


def _submit_locked(
    session: QuizSession, question_id: int, selected_option_id: int | None, now: datetime
) -> AnswerOutcome:
    if session.status == Status.ABANDONED:
        raise SessionExpired()
    if session.status != Status.IN_PROGRESS:
        raise SessionAlreadyFinished()

    sq = _current_sq(session)
    if sq.question_id != question_id or sq.answered_at is not None:
        raise AlreadyAnswered(
            details={"question_id": question_id, "expected_question_id": sq.question_id}
        )

    options = list(sq.question.options.all())
    correct = next(o for o in options if o.is_correct)
    selected: AnswerOption | None = None
    if selected_option_id is not None:
        selected = next((o for o in options if o.id == selected_option_id), None)
        if selected is None:
            raise ValidationError({"selected_option_id": ["Bu şık bu soruya ait değil."]})

    if sq.served_at is None:  # normalde olmaz; savunma amaçlı
        sq.served_at = now
    elapsed = elapsed_ms_between(sq.served_at, now)

    if selected is None or elapsed > acceptance_window_ms():
        outcome, points = Outcome.TIMEOUT, 0
        session.timeout_count += 1
    elif selected.is_correct:
        outcome, points = Outcome.CORRECT, compute_points(elapsed)
        session.correct_count += 1
        Question.objects.filter(pk=sq.question_id).update(times_correct=F("times_correct") + 1)
    else:
        outcome, points = Outcome.WRONG, 0
        session.wrong_count += 1

    sq.selected_option = selected
    sq.answered_at = now
    sq.elapsed_ms = elapsed
    sq.outcome = outcome
    sq.is_correct = outcome == Outcome.CORRECT
    sq.points = points
    sq.save()

    session.score += points
    session.current_index += 1

    next_question = None
    if session.current_index >= session.total_questions:
        _finalize(session, now)
    else:
        session.save()
        next_question = _serve(_current_sq(session), now)

    result = AnswerResult(
        outcome=outcome,
        is_correct=outcome == Outcome.CORRECT,
        correct_option_id=correct.id,
        selected_option_id=selected.id if selected else None,
        elapsed_ms=elapsed,
        points_earned=points,
        explanation=sq.question.explanation,
    )
    return AnswerOutcome(session=session, result=result, next_question=next_question)


# ---------------------------------------------------------------------------
# Özet (§7.7)
# ---------------------------------------------------------------------------


def session_elapsed_stats(session: QuizSession) -> dict:
    """Süre istatistikleri (D15): timeout 5000 ms sayılır; ortalama yalnızca cevaplananlardan."""
    limit = _cfg("TIME_LIMIT_MS")
    rows = list(session.questions.values_list("outcome", "elapsed_ms"))
    total = 0
    answered = []
    fastest = None
    for outcome, elapsed in rows:
        if outcome in (Outcome.CORRECT, Outcome.WRONG):
            clamped = clamp_elapsed(elapsed or 0)
            total += clamped
            answered.append(clamped)
            if outcome == Outcome.CORRECT and (fastest is None or clamped < fastest):
                fastest = clamped
        else:
            total += limit
    return {
        "total_elapsed_ms": total,
        "average_elapsed_ms": round(sum(answered) / len(answered)) if answered else None,
        "fastest_correct_ms": fastest,
    }


def build_summary(session: QuizSession) -> dict:
    from apps.leaderboard import services as leaderboard

    if session.status != Status.COMPLETED:
        raise SessionNotFinished()

    stats = session_elapsed_stats(session)
    entry = getattr(session, "leaderboard_entry", None)
    if entry is not None:
        rank = leaderboard.rank_of_entry(entry, category=session.category)
    else:
        rank = leaderboard.estimated_rank(
            session.category, session.score, stats["total_elapsed_ms"]
        )
    total = session.total_questions
    max_per_question = _cfg("BASE_POINTS") + _cfg("MAX_SPEED_BONUS")
    return {
        "session_id": session.id,
        "category": session.category,
        "status": session.status,
        "score": session.score,
        "max_possible_score": total * max_per_question,
        "total_questions": total,
        "correct_count": session.correct_count,
        "wrong_count": session.wrong_count,
        "timeout_count": session.timeout_count,
        "accuracy_pct": round(100 * session.correct_count / total, 1) if total else 0.0,
        **stats,
        "score_submitted": entry is not None,
        "estimated_rank": rank,
        "finished_at": session.finished_at,
    }


# ---------------------------------------------------------------------------
# Bakım (§8.4)
# ---------------------------------------------------------------------------


def abandon_stale_sessions(now: datetime | None = None) -> int:
    now = now or timezone.now()
    return QuizSession.objects.filter(status=Status.IN_PROGRESS, expires_at__lt=now).update(
        status=Status.ABANDONED
    )
