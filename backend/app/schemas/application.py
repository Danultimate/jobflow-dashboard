from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationBase(BaseModel):
    job_posting_id: int
    status: str = "saved"
    notes: str | None = None
    applied_at: datetime | None = None
    last_response_at: datetime | None = None
    next_follow_up_at: datetime | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    applied_at: datetime | None = None
    last_response_at: datetime | None = None
    next_follow_up_at: datetime | None = None


class StatusTransition(BaseModel):
    status: str = Field(..., description="Next application status")
    note: str | None = None


class ApplicationRead(ApplicationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
