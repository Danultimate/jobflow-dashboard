from datetime import datetime

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.reminder_service import get_due_follow_ups
from app.workers.celery_app import celery_app


@celery_app.task
def check_follow_ups() -> dict:
    db: Session = SessionLocal()
    try:
        due = get_due_follow_ups(db)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "due_follow_ups": len(due),
            "application_ids": [item.id for item in due],
        }
    finally:
        db.close()
