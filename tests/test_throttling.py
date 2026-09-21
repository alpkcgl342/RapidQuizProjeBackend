import pytest
from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle

pytestmark = pytest.mark.django_db


@pytest.fixture
def low_session_limit(monkeypatch):
    rates = {**api_settings.DEFAULT_THROTTLE_RATES, "session_create": "2/hour"}
    monkeypatch.setattr(SimpleRateThrottle, "THROTTLE_RATES", rates)


def _create(api, **meta):
    return api.post("/api/v1/quiz-sessions/", {"category": "yazilim"}, format="json", **meta)


def test_session_create_throttled_with_retry_after(api, category, low_session_limit):
    assert _create(api).status_code == 201
    assert _create(api).status_code == 201
    res = _create(api)
    assert res.status_code == 429
    assert res.json()["error"]["code"] == "RATE_LIMITED"
    assert int(res["Retry-After"]) > 0


def test_forwarded_ips_have_separate_counters(api, category, low_session_limit, settings):
    """Proxy arkasında farklı istemci IP'leri ayrı sayaç kullanmalı (§14.4)."""
    settings.IPWARE_META_PRECEDENCE_ORDER = (
        "HTTP_DO_CONNECTING_IP",
        "HTTP_X_FORWARDED_FOR",
        "REMOTE_ADDR",
    )
    a = {"HTTP_X_FORWARDED_FOR": "203.0.113.10, 10.0.0.1"}
    b = {"HTTP_X_FORWARDED_FOR": "198.51.100.20, 10.0.0.1"}
    assert _create(api, **a).status_code == 201
    assert _create(api, **a).status_code == 201
    assert _create(api, **a).status_code == 429
    assert _create(api, **b).status_code == 201

    c = {"HTTP_DO_CONNECTING_IP": "192.0.2.30", "HTTP_X_FORWARDED_FOR": "203.0.113.10"}
    assert _create(api, **c).status_code == 201
