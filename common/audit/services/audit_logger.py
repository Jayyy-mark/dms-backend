# common/audit/services/audit_logger.py
import logging

audit_logger = logging.getLogger("audit")

def log_event(*, user_id, action, resource, metadata=None):
    audit_logger.info({
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "metadata": metadata or {}
    })
