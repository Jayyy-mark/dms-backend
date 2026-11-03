import hashlib
import threading
import time
from django.http import JsonResponse


class DuplicateRequestGuardMiddleware:
    """
    Prevents simultaneous duplicate mutating requests (POST, PUT, PATCH, DELETE)
    from the same user/client to the same endpoint while the initial request is
    still in-flight.
    """

    MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    LOCK_TTL_SECONDS = 15.0

    _lock = threading.Lock()
    _in_flight: dict[str, float] = {}

    def __init__(self, get_response):
        self.get_response = get_response

    def _get_actor_key(self, request) -> str:
        jwt_payload = getattr(request, "jwt_payload", None)
        if isinstance(jwt_payload, dict) and jwt_payload.get("user_id"):
            return f"user:{jwt_payload['user_id']}"

        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            return f"user:{user.pk}"

        cookie_token = request.COOKIES.get("mogApp_cookie")
        if cookie_token:
            token_hash = hashlib.sha256(cookie_token.encode("utf-8")).hexdigest()[:16]
            return f"cookie:{token_hash}"

        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "anon")
        return f"ip:{ip}"

    def _build_fingerprint(self, request) -> str:
        actor = self._get_actor_key(request)
        method = (request.method or "").upper()
        path = request.path_info or request.path
        content_type = request.META.get("CONTENT_TYPE", "")

        body_sig = ""
        if "multipart/form-data" not in content_type.lower():
            try:
                raw_body = request.body or b""
                if len(raw_body) <= 65536:
                    body_sig = hashlib.sha256(raw_body).hexdigest()[:16]
            except Exception:
                body_sig = ""

        return f"{actor}:{method}:{path}:{body_sig}"

    def __call__(self, request):
        method = (request.method or "").upper()
        path = request.path_info or request.path

        if method not in self.MUTATING_METHODS or path.endswith("/token/refresh/"):
            return self.get_response(request)

        fingerprint = self._build_fingerprint(request)
        now = time.monotonic()

        with self._lock:
            expired_keys = [
                k for k, ts in self._in_flight.items() if now - ts > self.LOCK_TTL_SECONDS
            ]
            for k in expired_keys:
                self._in_flight.pop(k, None)

            if fingerprint in self._in_flight:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "A request is already in progress. Please wait.",
                        "detail": "A request is already in progress. Please wait.",
                    },
                    status=429,
                )

            self._in_flight[fingerprint] = now

        try:
            return self.get_response(request)
        finally:
            with self._lock:
                self._in_flight.pop(fingerprint, None)

