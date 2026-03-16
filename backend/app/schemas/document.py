from datetime import datetime

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    application_id: int
    kind: str
    title: str
    content: str


class DocumentRead(BaseModel):
    id: int
    application_id: int
    kind: str
    title: str
    content: str
    version: int
    created_at: datetime

    class Config:
        from_attributes = True
