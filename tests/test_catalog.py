import json

import pytest
from django.core.exceptions import ValidationError
from django.core.management import CommandError, call_command

from apps.catalog.models import AnswerOption, Category, Question, validate_option_set
from tests.factories import QuestionFactory, make_category_with_questions

pytestmark = pytest.mark.django_db


# --- Model kuralları ---


def test_option_set_valid():
    validate_option_set([("a", True), ("b", False), ("c", False), ("d", False)])


@pytest.mark.parametrize(
    "options",
    [
        [("a", True), ("b", False), ("c", False)],  # 3 şık
        [("a", True), ("b", True), ("c", False), ("d", False)],  # 2 doğru
        [("a", False), ("b", False), ("c", False), ("d", False)],  # doğru yok
        [("a", True), ("", False), ("c", False), ("d", False)],  # boş metin
    ],
)
def test_option_set_invalid(options):
    with pytest.raises(ValidationError):
        validate_option_set(options)


def test_question_clean_checks_saved_options():
    q = QuestionFactory()
    q.clean()
    AnswerOption.objects.filter(question=q, display_order=1).update(is_correct=True)
    with pytest.raises(ValidationError):
        q.clean()


# --- Kategoriler endpoint'i ---


def test_categories_endpoint(api):
    make_category_with_questions(20, slug="yazilim", name="Yazılım")
    small = make_category_with_questions(5, slug="fizik", name="Fizik")
    QuestionFactory.create_batch(3, category=small, is_active=False)

    res = api.get("/api/v1/categories/")
    assert res.status_code == 200
    by_slug = {c["slug"]: c for c in res.json()["results"]}
    assert by_slug["yazilim"]["available_question_count"] == 20
    assert by_slug["yazilim"]["is_playable"] is True
    assert by_slug["yazilim"]["questions_per_session"] == 20
    assert by_slug["fizik"]["available_question_count"] == 5  # pasifler sayılmaz
    assert by_slug["fizik"]["is_playable"] is False
    assert set(by_slug["yazilim"]) == {
        "slug",
        "name",
        "description",
        "color_hex",
        "icon",
        "questions_per_session",
        "available_question_count",
        "is_playable",
    }


def test_categories_ordered_by_display_order(api):
    make_category_with_questions(0, slug="ikinci", display_order=2)
    make_category_with_questions(0, slug="ucuncu", display_order=3)
    make_category_with_questions(0, slug="birinci", display_order=1)
    slugs = [c["slug"] for c in api.get("/api/v1/categories/").json()["results"]]
    assert slugs == ["birinci", "ikinci", "ucuncu"]


def test_inactive_category_hidden(api):
    make_category_with_questions(20, slug="gizli", is_active=False)
    assert api.get("/api/v1/categories/").json()["results"] == []


# --- Seed komutu ---


def test_seed_real_fixtures_is_idempotent():
    call_command("seed_questions")
    counts = (Category.objects.count(), Question.objects.count(), AnswerOption.objects.count())
    assert counts == (5, 100, 400)

    call_command("seed_questions")
    assert (
        Category.objects.count(),
        Question.objects.count(),
        AnswerOption.objects.count(),
    ) == counts

    for q in Question.objects.prefetch_related("options"):
        validate_option_set((o.text, o.is_correct) for o in q.options.all())


def _write_fixture(tmp_path, questions):
    data = {
        "category": {"slug": "deneme", "name": "Deneme", "color_hex": "#000000", "icon": "x"},
        "questions": questions,
    }
    (tmp_path / "deneme.json").write_text(json.dumps(data), encoding="utf-8")


def _q(ref, correct=1):
    return {
        "external_ref": ref,
        "text": f"{ref}?",
        "options": [{"text": f"o{i}", "is_correct": i < correct} for i in range(4)],
    }


def test_seed_updates_existing_question(tmp_path):
    _write_fixture(tmp_path, [_q("d-1")])
    call_command("seed_questions", dir=tmp_path)
    q = _q("d-1")
    q["text"] = "Güncel metin?"
    _write_fixture(tmp_path, [q])
    call_command("seed_questions", dir=tmp_path)
    assert Question.objects.get(external_ref="d-1").text == "Güncel metin?"
    assert Question.objects.count() == 1


def test_seed_rejects_invalid_fixture_without_writing(tmp_path):
    _write_fixture(tmp_path, [_q("d-1"), _q("d-2", correct=2)])
    with pytest.raises(CommandError, match="d-2"):
        call_command("seed_questions", dir=tmp_path)
    assert Question.objects.count() == 0


def test_seed_rejects_duplicate_ref(tmp_path):
    _write_fixture(tmp_path, [_q("d-1"), _q("d-1")])
    with pytest.raises(CommandError, match="tekrar"):
        call_command("seed_questions", dir=tmp_path)
