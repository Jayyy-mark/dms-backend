import time
import logging

logger = logging.getLogger("audit")

class AuditLogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        user_id = None
        if hasattr(request, "jwt_payload"):
            user_id = request.jwt_payload.get("user_id")

        logger.info({
            "user_id": user_id,
            "path": request.path,
            "method": request.method,
            "status": response.status_code,
            "duration_ms": int((time.time() - start_time) * 1000),
        })

        return response
