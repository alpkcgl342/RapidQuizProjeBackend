"""Takma ad doğrulama (§7.8). Küfür filtresi v1.0'da yoktur (D11)."""

import re

from django.core.exceptions import ValidationError

MIN_LENGTH = 2
MAX_LENGTH = 20

_ALLOWED = re.compile(r"^[A-Za-z0-9ÇĞİÖŞÜçğıöşüÂÎÛâîû_\- ]+$")
_SPACES = re.compile(r"\s+")


def normalize_nickname(value: str) -> str:
    """Baş/son boşlukları kırpar, ardışık boşlukları teke indirir."""
    return _SPACES.sub(" ", value).strip()


def validate_nickname(value: str) -> str:
    """Normalize edilmiş takma adı döner; kurala uymuyorsa ValidationError fırlatır."""
    nickname = normalize_nickname(value)
    if not MIN_LENGTH <= len(nickname) <= MAX_LENGTH:
        raise ValidationError(f"Takma ad {MIN_LENGTH}-{MAX_LENGTH} karakter olmalı.")
    if not _ALLOWED.match(nickname):
        raise ValidationError("Takma ad yalnızca harf, rakam, boşluk, _ ve - içerebilir.")
    return nickname
