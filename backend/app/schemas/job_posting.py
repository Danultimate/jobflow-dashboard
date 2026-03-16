from datetime import datetime

from pydantic import BaseModel


class JobPostingBase(BaseModel):
    source: str = "manual"
    external_id: str | None = None
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    url: str | None = None
    posted_at: datetime | None = None


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str | None = None
    url: str | None = None
    posted_at: datetime | None = None


class JobPostingRead(JobPostingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
