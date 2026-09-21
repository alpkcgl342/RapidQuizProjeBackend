import pytest
from django.core.exceptions import ValidationError

from common.nickname import validate_nickname


@pytest.mark.django_db
def test_health(api):
    res = api.get("/api/v1/health/")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["time"].endswith("Z")


@pytest.mark.django_db
def test_validation_error_envelope(api):
    res = api.get("/api/v1/leaderboard/?limit=999")
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "limit" in res.json()["error"]["details"]


@pytest.mark.django_db
def test_openapi_schema_generates(api):
    res = api.get("/api/schema/?format=json")
    assert res.status_code == 200
    paths = res.json()["paths"]
    assert "/api/v1/quiz-sessions/{id}/answers/" in paths


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("hizlisimsek", "hizlisimsek"),
        ("  Ayşe   Öz  ", "Ayşe Öz"),
        ("dev_ali-42", "dev_ali-42"),
        ("Çağrı İĞÜŞ", "Çağrı İĞÜŞ"),
    ],
)
def test_nickname_valid(raw, expected):
    assert validate_nickname(raw) == expected


@pytest.mark.parametrize("raw", ["a", "   ", "x" * 21, "ali<script>", "emoji😀", "a.b"])
def test_nickname_invalid(raw):
    with pytest.raises(ValidationError):
        validate_nickname(raw)
