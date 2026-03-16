from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ApplicationStatus(str, Enum):
    saved = "saved"
    prepared = "prepared"
    applied = "applied"
    recruiter_contact = "recruiter_contact"
    interview = "interview"
    rejected = "rejected"
    offer = "offer"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default=ApplicationStatus.saved.value, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_response_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_follow_up_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    job_posting = relationship("JobPosting", back_populates="applications")
    interviews = relationship("Interview", back_populates="application")
    documents = relationship("Document", back_populates="application")
    contacts = relationship("Contact", back_populates="application")
    activity_logs = relationship("ActivityLog", back_populates="application")
