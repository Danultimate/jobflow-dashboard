from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(50), default="manual", index=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    applications = relationship("Application", back_populates="job_posting")
