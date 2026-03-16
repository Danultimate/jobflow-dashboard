from pydantic import BaseModel
from fastapi import APIRouter

from app.services.linkedin_adapter import LinkedInAdapter

router = APIRouter(prefix="/linkedin", tags=["linkedin"])
adapter = LinkedInAdapter()


class AutomationApplyRequest(BaseModel):
    job_url: str


@router.post("/automation/apply")
def apply_via_automation(payload: AutomationApplyRequest) -> dict:
    return adapter.apply_via_automation(payload.job_url)
