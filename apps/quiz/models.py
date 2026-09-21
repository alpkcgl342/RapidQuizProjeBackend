import secrets
import uuid

from django.db import models

from apps.catalog.models import AnswerOption, Category, Question


def generate_token() -> str:
    return secrets.token_urlsafe(32)


class QuizSession(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "Devam ediyor"
        COMPLETED = "completed", "Tamamlandı"
        ABANDONED = "abandoned", "Terk edildi"

    class Platform(models.TextChoices):
        WEB = "web", "Web"
        IOS = "ios", "iOS"
        ANDROID = "android", "Android"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=64, unique=True, default=generate_token, editable=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="sessions")
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.IN_PROGRESS, db_index=True
    )
    total_questions = models.PositiveSmallIntegerField(default=20)
    current_index = models.PositiveSmallIntegerField(default=0)
    score = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveSmallIntegerField(default=0)
    wrong_count = models.PositiveSmallIntegerField(default=0)
    timeout_count = models.PositiveSmallIntegerField(default=0)
    client_platform = models.CharField(max_length=16, choices=Platform.choices, blank=True)
    client_version = models.CharField(max_length=20, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "quiz oturumu"
        verbose_name_plural = "quiz oturumları"

    def __str__(self) -> str:
        return f"{self.category} · {self.get_status_display()} · {self.score}"


class QuizSessionQuestion(models.Model):
    class Outcome(models.TextChoices):
        PENDING = "pending", "Bekliyor"
        CORRECT = "correct", "Doğru"
        WRONG = "wrong", "Yanlış"
        TIMEOUT = "timeout", "Süre doldu"

    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name="questions")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="+")
    order = models.PositiveSmallIntegerField()
    served_at = models.DateTimeField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    selected_option = models.ForeignKey(
        AnswerOption, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    is_correct = models.BooleanField(null=True)
    elapsed_ms = models.PositiveIntegerField(null=True, blank=True)
    points = models.PositiveSmallIntegerField(default=0)
    outcome = models.CharField(max_length=10, choices=Outcome.choices, default=Outcome.PENDING)

    class Meta:
        ordering = ["session", "order"]
        constraints = [
            models.UniqueConstraint(fields=["session", "order"], name="uniq_session_order"),
            models.UniqueConstraint(fields=["session", "question"], name="uniq_session_question"),
        ]
        verbose_name = "oturum sorusu"
        verbose_name_plural = "oturum soruları"

    def __str__(self) -> str:
        return f"#{self.order + 1} · {self.get_outcome_display()}"
