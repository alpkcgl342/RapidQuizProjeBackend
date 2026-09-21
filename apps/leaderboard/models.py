from django.db import models

from apps.catalog.models import Category
from apps.quiz.models import QuizSession

# Sıralama kuralı (§6.2): puan azalan → toplam süre artan → önce kaydeden → id.
RANK_ORDERING = ["-score", "total_elapsed_ms", "created_at", "id"]


class LeaderboardEntry(models.Model):
    session = models.OneToOneField(
        QuizSession, on_delete=models.CASCADE, related_name="leaderboard_entry"
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="+")
    nickname = models.CharField(max_length=20, db_index=True)
    score = models.PositiveIntegerField(db_index=True)
    correct_count = models.PositiveSmallIntegerField()
    total_elapsed_ms = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = RANK_ORDERING
        indexes = [
            models.Index(
                "category",
                models.F("score").desc(),
                "total_elapsed_ms",
                name="lb_category_rank_idx",
            ),
            models.Index(models.F("score").desc(), "total_elapsed_ms", name="lb_overall_rank_idx"),
        ]
        verbose_name = "skor kaydı"
        verbose_name_plural = "skor kayıtları"

    def __str__(self) -> str:
        return f"{self.nickname} · {self.score}"
