from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission

from common.exceptions import InvalidSessionToken, SessionNotOwned

from .models import QuizSession

HEADER = "HTTP_X_SESSION_TOKEN"


class SessionTokenAuthentication(BaseAuthentication):
    """X-Session-Token başlığını QuizSession'a çözer (§8.2).

    Django user'ı YOK: `request.auth` ve `request.quiz_session` oturumu taşır.
    Başlık yoksa None döner (permission 401 üretir); geçersizse 401 fırlatır.
    Süre kontrolü (410) servis katmanında yapılır.
    """

    def authenticate(self, request):
        token = request.META.get(HEADER, "").strip()
        if not token:
            return None
        session = QuizSession.objects.select_related("category").filter(token=token).first()
        if session is None:
            raise InvalidSessionToken()
        request._request.quiz_session = session
        return (None, session)

    def authenticate_header(self, request):
        # 401'in 403'e dönüşmemesi için WWW-Authenticate değeri gerekir.
        return "Session-Token"


class IsSessionOwner(BasePermission):
    """URL'deki oturum id'si token'ın oturumuyla eşleşmeli; aksi halde 403."""

    def has_permission(self, request, view):
        session = request.auth
        if not isinstance(session, QuizSession):
            return False
        if str(view.kwargs.get("pk")) != str(session.pk):
            raise SessionNotOwned()
        return True


class SessionTokenScheme(OpenApiAuthenticationExtension):
    target_class = SessionTokenAuthentication
    name = "SessionToken"

    def get_security_definition(self, auto_schema):
        return {"type": "apiKey", "in": "header", "name": "X-Session-Token"}
