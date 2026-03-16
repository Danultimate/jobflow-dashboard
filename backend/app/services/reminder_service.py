from datetime import datetime, timedelta

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.application import Application


def get_due_follow_ups(db: Session) -> list[Application]:
    now = datetime.utcnow()
    query: Select[tuple[Application]] = select(Application).where(
        Application.next_follow_up_at.is_not(None),
        Application.next_follow_up_at <= now,
    )
    return list(db.scalars(query).all())


def set_default_follow_up(application: Application, days: int = 7) -> None:
    if application.next_follow_up_at is None:
        application.next_follow_up_at = datetime.utcnow() + timedelta(days=days)
