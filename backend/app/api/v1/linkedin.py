from typing import Any

from celery.result import AsyncResult
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.services.linkedin_automation import (
    normalize_cookies,
    parse_cookie_header,
    store_session,
)
from app.workers.celery_app import celery_app
from app.workers.tasks import apply_linkedin_draft

router = APIRouter(prefix="/linkedin", tags=["linkedin"])
settings = get_settings()


class AutomationApplyRequest(BaseModel):
    job_url: str
    session_id: str = "default"
    draft: dict[str, Any] = Field(default_factory=dict)


class AutomationSessionBootstrapRequest(BaseModel):
    session_id: str = "default"
    cookies: list[dict[str, Any]] | None = None
    cookies_json: str | None = None
    cookie_header: str | None = None
    user_agent: str | None = None


def _ensure_enabled() -> None:
    if not settings.enable_automation:
        raise HTTPException(
            status_code=400,
            detail="Automation is disabled. Enable with ENABLE_AUTOMATION=true.",
        )


@router.post("/automation/session/bootstrap")
def bootstrap_session(payload: AutomationSessionBootstrapRequest) -> dict:
    _ensure_enabled()
    parsed_cookies = normalize_cookies(payload.cookies)
    if not parsed_cookies and payload.cookies_json:
        import json

        try:
            parsed_cookies = normalize_cookies(json.loads(payload.cookies_json))
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid cookies_json payload.") from exc
    if not parsed_cookies and payload.cookie_header:
        parsed_cookies = parse_cookie_header(payload.cookie_header)
    if not parsed_cookies:
        raise HTTPException(status_code=400, detail="No valid cookies supplied.")
    data = store_session(payload.session_id, parsed_cookies, payload.user_agent)
    return {"ok": True, **data}


@router.post("/automation/apply")
def apply_via_automation(payload: AutomationApplyRequest) -> dict:
    _ensure_enabled()
    task = apply_linkedin_draft.delay(
        job_url=payload.job_url,
        session_id=payload.session_id,
        draft=payload.draft,
    )
    return {"ok": True, "task_id": task.id, "status": "queued"}


@router.get("/automation/tasks/{task_id}")
def automation_task_status(task_id: str) -> dict:
    result = AsyncResult(task_id, app=celery_app)
    payload: Any = result.result if result.ready() else None
    return {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else False,
        "result": payload,
    }
