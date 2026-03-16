from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.activity_log import ActivityLog
from app.models.application import Application
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentRead

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRead])
def list_documents(application_id: int | None = None, db: Session = Depends(db_session)) -> list[Document]:
    query: Select[tuple[Document]] = select(Document).order_by(Document.created_at.desc())
    if application_id:
        query = query.where(Document.application_id == application_id)
    return list(db.scalars(query).all())


@router.post("", response_model=DocumentRead)
def create_document(payload: DocumentCreate, db: Session = Depends(db_session)) -> Document:
    app = db.get(Application, payload.application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    latest = db.scalar(
        select(Document).where(
            Document.application_id == payload.application_id,
            Document.kind == payload.kind,
        ).order_by(Document.version.desc())
    )
    version = (latest.version + 1) if latest else 1
    entity = Document(**payload.model_dump(), version=version)
    db.add(entity)
    db.add(
        ActivityLog(
            application=app,
            event_type="document_created",
            message=f"Created {payload.kind} document version {version}.",
        )
    )
    db.commit()
    db.refresh(entity)
    return entity
