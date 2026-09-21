"""Aynı soruya eşzamanlı iki cevap: yalnızca biri işlenmeli (§8.3)."""

import threading

import pytest
from django.db import connection

from apps.quiz import services
from apps.quiz.models import QuizSession
from common.exceptions import AlreadyAnswered
from tests.factories import make_category_with_questions


@pytest.mark.django_db(transaction=True)
def test_parallel_answers_only_one_wins():
    category = make_category_with_questions(20, slug="yazilim")
    session, served = services.create_session(category.slug)
    correct = session.questions.get(order=0).question.options.get(is_correct=True).id

    barrier = threading.Barrier(2)
    results: list[str] = []

    def worker():
        try:
            barrier.wait()
            s = QuizSession.objects.get(pk=session.pk)
            services.submit_answer(s, served.id, correct)
            results.append("ok")
        except AlreadyAnswered:
            results.append("conflict")
        finally:
            connection.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(results) == ["conflict", "ok"]
    session.refresh_from_db()
    assert session.current_index == 1
    assert session.correct_count == 1
