# backend/app/tasks/session_cleanup.py

import logging
from celery import shared_task
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..session_manager import session_manager

logger = logging.getLogger(__name__)

@shared_task
def cleanup_expired_sessions():
    """
    Scheduled task to clean up expired sessions.
    Requirements: 2D.2
    """
    db = SessionLocal()
    try:
        expired_count = session_manager.cleanup_expired_sessions(db)
        logger.info(f"Scheduled task: Cleaned up {expired_count} expired sessions")
        return expired_count
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        raise
    finally:
        db.close()