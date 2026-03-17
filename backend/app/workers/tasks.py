from datetime import datetime

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.linkedin_automation import load_session
from app.services.reminder_service import get_due_follow_ups
from app.workers.celery_app import celery_app


@celery_app.task
def check_follow_ups() -> dict:
    db: Session = SessionLocal()
    try:
        due = get_due_follow_ups(db)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "due_follow_ups": len(due),
            "application_ids": [item.id for item in due],
        }
    finally:
        db.close()


def _fill_first(page: object, selectors: list[str], value: str, actions: list[str]) -> None:
    if not value:
        return
    for selector in selectors:
        locator = page.locator(selector)  # type: ignore[attr-defined]
        if locator.count() > 0:
            locator.first.fill(value)
            actions.append(f"filled:{selector}")
            return


@celery_app.task
def apply_linkedin_draft(job_url: str, session_id: str = "default", draft: dict | None = None) -> dict:
    settings = get_settings()
    if not settings.enable_automation:
        return {
            "ok": False,
            "message": "Automation is disabled. Enable with ENABLE_AUTOMATION=true.",
        }

    session = load_session(session_id)
    if not session:
        return {
            "ok": False,
            "message": "No valid LinkedIn session found. Bootstrap cookies first.",
        }

    payload = draft or {}
    actions: list[str] = []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=settings.automation_headless)
            context = browser.new_context(user_agent=session.get("user_agent") or settings.automation_user_agent)
            context.add_cookies(session["cookies"])
            page = context.new_page()
            page.goto(job_url, wait_until="domcontentloaded", timeout=settings.automation_timeout_ms)
            actions.append("opened_job")

            for selector in ["button.jobs-apply-button", "button[aria-label*='Easy Apply']"]:
                locator = page.locator(selector)
                if locator.count() > 0:
                    locator.first.click()
                    actions.append(f"clicked:{selector}")
                    break

            _fill_first(
                page,
                ["input[name*='name' i]", "input[id*='name' i]"],
                str(payload.get("full_name", "")),
                actions,
            )
            _fill_first(
                page,
                ["input[type='email']", "input[name*='email' i]"],
                str(payload.get("email", "")),
                actions,
            )
            _fill_first(
                page,
                ["input[type='tel']", "input[name*='phone' i]"],
                str(payload.get("phone", "")),
                actions,
            )
            _fill_first(
                page,
                ["textarea[name*='cover' i]", "textarea", "div[contenteditable='true']"],
                str(payload.get("cover_letter", "")),
                actions,
            )

            current_url = page.url
            page_title = page.title()
            context.close()
            browser.close()
    except PlaywrightTimeoutError as exc:
        return {"ok": False, "message": f"Playwright timeout: {exc!s}", "actions": actions}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"Automation error: {exc!s}", "actions": actions}

    return {
        "ok": True,
        "message": "Draft prefill workflow executed.",
        "actions": actions,
        "current_url": current_url,
        "title": page_title,
    }
