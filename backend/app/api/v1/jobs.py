from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.job_posting import JobPosting
from app.schemas.job_posting import JobPostingCreate, JobPostingRead, JobPostingUpdate
from app.services.linkedin_adapter import LinkedInAdapter

router = APIRouter(prefix="/jobs", tags=["jobs"])
linkedin_adapter = LinkedInAdapter()


@router.get("", response_model=list[JobPostingRead])
def list_jobs(q: str | None = None, db: Session = Depends(db_session)) -> list[JobPosting]:
    query: Select[tuple[JobPosting]] = select(JobPosting)
    if q:
        query = query.where(or_(JobPosting.title.ilike(f"%{q}%"), JobPosting.company.ilike(f"%{q}%")))
    return list(db.scalars(query.order_by(JobPosting.created_at.desc())).all())


@router.post("", response_model=JobPostingRead)
def create_job(payload: JobPostingCreate, db: Session = Depends(db_session)) -> JobPosting:
    entity = JobPosting(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.post("/import", response_model=JobPostingRead)
def import_job(payload: dict, db: Session = Depends(db_session)) -> JobPosting:
    normalized = linkedin_adapter.normalize_manual_import(payload)
    if normalized.external_id:
        existing = db.scalar(
            select(JobPosting).where(
                JobPosting.source == normalized.source,
                JobPosting.external_id == normalized.external_id,
            )
        )
        if existing:
            return existing
    entity = JobPosting(**normalized.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.get("/{job_id}", response_model=JobPostingRead)
def get_job(job_id: int, db: Session = Depends(db_session)) -> JobPosting:
    entity = db.get(JobPosting, job_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Job not found")
    return entity


@router.patch("/{job_id}", response_model=JobPostingRead)
def update_job(job_id: int, payload: JobPostingUpdate, db: Session = Depends(db_session)) -> JobPosting:
    entity = db.get(JobPosting, job_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Job not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity
