from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

import redis

from app.core.config import get_settings


def _redis_client() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _session_key(session_id: str) -> str:
    return f"linkedin:session:{session_id}"


def parse_cookie_header(cookie_header: str) -> list[dict[str, Any]]:
    cookies: list[dict[str, Any]] = []
    for part in cookie_header.split(";"):
        piece = part.strip()
        if "=" not in piece:
            continue
        name, value = piece.split("=", 1)
        if not name:
            continue
        cookies.append(
            {
                "name": name.strip(),
                "value": value.strip(),
                "domain": ".linkedin.com",
                "path": "/",
            }
        )
    return cookies


def normalize_cookies(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, dict) and "cookies" in raw:
        raw = raw["cookies"]
    if not isinstance(raw, Iterable) or isinstance(raw, (str, bytes, dict)):
        return []
    normalized: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        value = item.get("value")
        if not name or value is None:
            continue
        normalized.append(
            {
                "name": str(name),
                "value": str(value),
                "domain": str(item.get("domain") or ".linkedin.com"),
                "path": str(item.get("path") or "/"),
                "httpOnly": bool(item.get("httpOnly", False)),
                "secure": bool(item.get("secure", True)),
                "sameSite": str(item.get("sameSite") or "Lax"),
            }
        )
    return normalized


def store_session(
    session_id: str,
    cookies: list[dict[str, Any]],
    user_agent: str | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    payload = {
        "cookies": cookies,
        "user_agent": user_agent,
    }
    client = _redis_client()
    client.setex(
        _session_key(session_id),
        settings.linkedin_session_ttl_seconds,
        json.dumps(payload),
    )
    return {"session_id": session_id, "cookie_count": len(cookies)}


def load_session(session_id: str) -> dict[str, Any] | None:
    client = _redis_client()
    raw = client.get(_session_key(session_id))
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    cookies = normalize_cookies(parsed.get("cookies"))
    if not cookies:
        return None
    return {"cookies": cookies, "user_agent": parsed.get("user_agent")}
