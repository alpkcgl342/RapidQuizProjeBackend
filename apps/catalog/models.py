from collections.abc import Iterable

from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, RegexValidator
from django.db import models

OPTIONS_PER_QUESTION = 4


def validate_option_set(options: Iterable[tuple[str, bool]]) -> None:
    """Bir sorunun şık kümesini doğrular: tam 4 şık, tam 1 doğru, boş metin yok.

    `options`: (metin, doğru_mu) çiftleri. Model, admin formset'i ve seed komutu
    bu tek fonksiyonu kullanır.
    """
    options = list(options)
    errors = []
    if len(options) != OPTIONS_PER_QUESTION:
        errors.append(f"Soru tam {OPTIONS_PER_QUESTION} şıktan oluşmalı (şu an {len(options)}).")
    correct = sum(1 for _, is_correct in options if is_correct)
    if correct != 1:
        errors.append(f"Soru tam 1 doğru şık içermeli (şu an {correct}).")
    if any(not (text or "").strip() for text, _ in options):
        errors.append("Şık metni boş olamaz.")
    if errors:
        raise ValidationError(errors)


class Category(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=200, blank=True)
    color_hex = models.CharField(
        max_length=7,
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Renk #RRGGBB formatında olmalı.")],
    )
    icon = models.CharField(max_length=40)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "kategori"
        verbose_name_plural = "kategoriler"

    def __str__(self) -> str:
        return self.name


class Question(models.Model):
    class Difficulty(models.IntegerChoices):
        EASY = 1, "Kolay"
        MEDIUM = 2, "Orta"
        HARD = 3, "Zor"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="questions")
    external_ref = models.CharField(max_length=40, unique=True, null=True, blank=True)
    text = models.TextField(validators=[MaxLengthValidator(300)])
    explanation = models.TextField(blank=True)
    difficulty = models.SmallIntegerField(choices=Difficulty.choices, default=Difficulty.MEDIUM)
    is_active = models.BooleanField(default=True, db_index=True)
    times_served = models.PositiveIntegerField(default=0)
    times_correct = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "id"]
        indexes = [models.Index(fields=["category", "is_active"], name="question_cat_active_idx")]
        verbose_name = "soru"
        verbose_name_plural = "sorular"

    def __str__(self) -> str:
        return self.text[:80]

    def clean(self) -> None:
        # Kayıtlı soruda şıkları doğrula. Yeni soruda şıklar henüz yok; admin'de
        # inline formset, seed'de komut aynı kuralı uygular.
        if self.pk:
            validate_option_set(self.options.values_list("text", "is_correct"))


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    display_order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["question", "display_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["question", "display_order"], name="uniq_option_order_per_question"
            )
        ]
        verbose_name = "şık"
        verbose_name_plural = "şıklar"

    def __str__(self) -> str:
        return self.text
