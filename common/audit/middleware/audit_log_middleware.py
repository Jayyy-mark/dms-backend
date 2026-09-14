# common/audit/middleware/audit_log_middleware.py
import time
from common.audit.services.audit_logger import log_event

class AuditLogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)

        user_id = None
        if hasattr(request, "jwt_payload"):
            user_id = request.jwt_payload.get("user_id")

        log_event(
            user_id=user_id,
            action=request.method,
            resource=request.path,
            metadata={
                "status": response.status_code,
                "duration_ms": int((time.time() - start) * 1000)
            }
        )

        return response
