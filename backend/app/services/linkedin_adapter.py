from app.core.config import get_settings
from app.schemas.job_posting import JobPostingCreate


class LinkedInAdapter:
    """
    Compliant-first adapter.
    - Ingestion can happen via manual/API-supported import paths.
    - Automation calls are blocked by default and feature-flagged.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def normalize_manual_import(self, payload: dict) -> JobPostingCreate:
        return JobPostingCreate(
            source=payload.get("source", "linkedin_manual"),
            external_id=payload.get("external_id"),
            title=payload["title"],
            company=payload["company"],
            location=payload.get("location"),
            description=payload.get("description"),
            url=payload.get("url"),
            posted_at=payload.get("posted_at"),
        )

    def apply_via_automation(self, _job_url: str) -> dict:
        if not self.settings.enable_automation:
            return {
                "enabled": False,
                "message": "Automation is disabled. Enable with ENABLE_AUTOMATION=true.",
            }
        return {
            "enabled": True,
            "message": "Automation adapter placeholder executed. Implement browser worker here.",
        }
