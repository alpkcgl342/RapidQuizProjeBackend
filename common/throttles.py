"""IP bazlı throttle sınıfları (§8.5). IP, django-ipware ile çözülür (§14.4)."""

from rest_framework.throttling import SimpleRateThrottle

from common.ip import get_client_ip


class ClientIpRateThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        ident = get_client_ip(request) or "unknown"
        return self.cache_format % {"scope": self.scope, "ident": ident}


class SessionCreateThrottle(ClientIpRateThrottle):
    scope = "session_create"


class AnswerThrottle(ClientIpRateThrottle):
    scope = "answer"


class ScoreSubmitThrottle(ClientIpRateThrottle):
    scope = "score_submit"


class AnonReadThrottle(ClientIpRateThrottle):
    scope = "anon_read"
