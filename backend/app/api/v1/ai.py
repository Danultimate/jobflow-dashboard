from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.application import Application
from app.models.document import Document
from app.schemas.document import DocumentRead
from app.services.llm_service import LLMService

router = APIRouter(prefix="/ai", tags=["ai"])
llm = LLMService()


class FitScoreRequest(BaseModel):
    application_id: int
    profile_context: str
    job_description: str | None = None


class CoverLetterRequest(BaseModel):
    application_id: int
    profile_context: str
    company: str
    role: str
    job_description: str


class ReviewRequest(BaseModel):
    application_id: int
    resume_text: str
    cover_letter: str
    job_description: str


class AIResponse(BaseModel):
    result: str


@router.post("/fit-score", response_model=AIResponse)
async def fit_score(payload: FitScoreRequest, db: Session = Depends(db_session)) -> AIResponse:
    app = db.get(Application, payload.application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    job_desc = payload.job_description or app.job_posting.description or ""
    result = await llm.score_job_fit(payload.profile_context, job_desc)
    return AIResponse(result=result)


@router.post("/cover-letter", response_model=DocumentRead)
async def cover_letter(payload: CoverLetterRequest, db: Session = Depends(db_session)) -> Document:
    app = db.get(Application, payload.application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    text = await llm.draft_cover_letter(
        profile=payload.profile_context,
        company=payload.company,
        role=payload.role,
        job_description=payload.job_description,
    )
    latest = db.query(Document).filter(
        Document.application_id == payload.application_id,
        Document.kind == "cover_letter",
    ).order_by(Document.version.desc()).first()
    entity = Document(
        application_id=payload.application_id,
        kind="cover_letter",
        title=f"Cover Letter - {payload.company}",
        content=text,
        version=(latest.version + 1) if latest else 1,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.post("/review", response_model=AIResponse)
async def review(payload: ReviewRequest, db: Session = Depends(db_session)) -> AIResponse:
    app = db.get(Application, payload.application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    result = await llm.review_application(
        resume_text=payload.resume_text,
        cover_letter=payload.cover_letter,
        job_description=payload.job_description,
    )
    return AIResponse(result=result)
