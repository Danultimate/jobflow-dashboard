from datetime import datetime

from pydantic import BaseModel


class TimestampedModel(BaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
