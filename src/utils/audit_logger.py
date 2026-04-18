import logging
from datetime import datetime
from typing import Optional, Any

logger = logging.getLogger(__name__)


class AuditLogger:
    def __init__(self, db_session: Any):
        self.db = db_session

    def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log user action for compliance."""
        log_entry = {
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details,
            'ip_address': ip_address,
            'created_at': datetime.utcnow().isoformat()
        }
        try:
            self.db.execute(
                "INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address, created_at) "
                "VALUES (:user_id, :action, :resource_type, :resource_id, :details, :ip_address, :created_at)",
                log_entry)
            self.db.commit()
        except Exception as exc:
            logger.error(f"Failed to write audit log: {exc}")
