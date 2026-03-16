from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
import httpx
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


def _raise_llm_unavailable(exc: Exception) -> None:
    detail = "LLM service unavailable. Verify OLLAMA_BASE_URL/OLLAMA_MODEL and Ollama container health."
    if isinstance(exc, httpx.HTTPStatusError):
        detail = f"{detail} Upstream status: {exc.response.status_code}."
    raise HTTPException(status_code=502, detail=detail) from exc


@router.post("/fit-score", response_model=AIResponse)
async def fit_score(payload: FitScoreRequest, db: Session = Depends(db_session)) -> AIResponse:
    app = db.get(Application, payload.application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    job_desc = payload.job_description or (app.job_posting.description if app.job_posting else "") or ""
    try:
        result = await llm.score_job_fit(payload.profile_context, job_desc)
    except (httpx.HTTPError, ValueError) as exc:
        _raise_llm_unavailable(exc)
    return AIResponse(result=result)


@router.post("/cover-letter", response_model=DocumentRead)
async def cover_letter(payload: CoverLetterRequest, db: Session = Depends(db_session)) -> Document:
    app = db.get(Application, payload.application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    try:
        text = await llm.draft_cover_letter(
            profile=payload.profile_context,
            company=payload.company,
            role=payload.role,
            job_description=payload.job_description,
        )
    except (httpx.HTTPError, ValueError) as exc:
        _raise_llm_unavailable(exc)
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
    try:
        result = await llm.review_application(
            resume_text=payload.resume_text,
            cover_letter=payload.cover_letter,
            job_description=payload.job_description,
        )
    except (httpx.HTTPError, ValueError) as exc:
        _raise_llm_unavailable(exc)
    return AIResponse(result=result)
