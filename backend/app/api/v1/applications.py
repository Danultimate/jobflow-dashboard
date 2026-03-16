from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import db_session
from app.models.activity_log import ActivityLog
from app.models.application import Application
from app.models.job_posting import JobPosting
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    StatusTransition,
)
from app.schemas.dashboard import DashboardMetrics
from app.services.reminder_service import set_default_follow_up

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationRead])
def list_applications(db: Session = Depends(db_session)) -> list[Application]:
    query: Select[tuple[Application]] = select(Application).order_by(Application.updated_at.desc())
    return list(db.scalars(query).all())


@router.post("", response_model=ApplicationRead)
def create_application(payload: ApplicationCreate, db: Session = Depends(db_session)) -> Application:
    job = db.get(JobPosting, payload.job_posting_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    entity = Application(**payload.model_dump())
    set_default_follow_up(entity)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    try:
        db.add(
            ActivityLog(
                application_id=entity.id,
                event_type="application_created",
                message=f"Application created for {job.company} - {job.title}.",
            )
        )
        db.commit()
    except SQLAlchemyError:
        # Logging should not block the primary user action.
        db.rollback()
    return entity


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: Session = Depends(db_session)) -> Application:
    entity = db.get(Application, application_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Application not found")
    return entity


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: int, payload: ApplicationUpdate, db: Session = Depends(db_session)
) -> Application:
    entity = db.get(Application, application_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.add(
        ActivityLog(
            application=entity,
            event_type="application_updated",
            message="Application fields updated.",
        )
    )
    db.commit()
    db.refresh(entity)
    return entity


@router.post("/{application_id}/transition", response_model=ApplicationRead)
def transition_status(
    application_id: int, payload: StatusTransition, db: Session = Depends(db_session)
) -> Application:
    entity = db.get(Application, application_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Application not found")

    entity.status = payload.status
    if payload.status == "applied" and entity.applied_at is None:
        entity.applied_at = datetime.utcnow()
    if payload.status in {"recruiter_contact", "interview", "offer", "rejected"}:
        entity.last_response_at = datetime.utcnow()

    db.add(
        ActivityLog(
            application=entity,
            event_type="status_transition",
            message=payload.note or f"Status changed to {payload.status}.",
        )
    )
    db.commit()
    db.refresh(entity)
    return entity


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def dashboard_metrics(db: Session = Depends(db_session)) -> DashboardMetrics:
    total = db.scalar(select(func.count(Application.id))) or 0
    applied = db.scalar(select(func.count(Application.id)).where(Application.status == "applied")) or 0
    interviews = (
        db.scalar(select(func.count(Application.id)).where(Application.status == "interview")) or 0
    )
    responded = (
        db.scalar(
            select(func.count(Application.id)).where(Application.last_response_at.is_not(None))
        )
        or 0
    )
    pending_follow_ups = (
        db.scalar(
            select(func.count(Application.id)).where(
                Application.next_follow_up_at.is_not(None),
                Application.next_follow_up_at <= datetime.utcnow(),
            )
        )
        or 0
    )
    response_rate = float(responded / total) if total else 0.0

    return DashboardMetrics(
        total_applications=total,
        applied_count=applied,
        interview_count=interviews,
        response_rate=response_rate,
        pending_follow_ups=pending_follow_ups,
    )
