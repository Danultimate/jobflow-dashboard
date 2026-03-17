from __future__ import annotations

import json
import re

import httpx

from app.core.config import get_settings


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate(self, prompt: str, temperature: float = 0.2) -> str:
        body = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        timeout = float(self.settings.ollama_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.settings.ollama_base_url}/api/generate",
                json=body,
            )
            response.raise_for_status()
            data = response.json()
        return data.get("response", "").strip()

    async def score_job_fit(self, profile: str, job_description: str) -> str:
        prompt = (
            "You are a strict career assistant.\n"
            "Return plain text only (no JSON, no markdown code fences) using this format:\n"
            "Fit score: <0-100>\n"
            "Strengths: <comma-separated>\n"
            "Risks: <comma-separated>\n"
            "Missing keywords: <comma-separated>\n\n"
            f"Profile:\n{profile}\n\nJob Description:\n{job_description}"
        )
        raw = await self.generate(prompt, temperature=0.1)
        return self._format_fit_score_response(raw)

    async def draft_cover_letter(
        self, profile: str, company: str, role: str, job_description: str
    ) -> str:
        prompt = (
            "Write a one-page tailored cover letter. Keep it professional and concrete.\n"
            f"Company: {company}\nRole: {role}\n\nProfile:\n{profile}\n\n"
            f"Job Description:\n{job_description}"
        )
        return await self.generate(prompt, temperature=0.3)

    async def review_application(self, resume_text: str, cover_letter: str, job_description: str) -> str:
        prompt = (
            "Review this application package. Return: strengths, red_flags, "
            "improvement_actions, and final_recommendation.\n\n"
            f"Resume:\n{resume_text}\n\nCover Letter:\n{cover_letter}\n\n"
            f"Job Description:\n{job_description}"
        )
        return await self.generate(prompt, temperature=0.1)

    def _format_fit_score_response(self, response: str) -> str:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned).strip()
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            return cleaned
        if not isinstance(parsed, dict):
            return cleaned

        score = parsed.get("fit_score_0_100", "N/A")
        strengths = parsed.get("strengths", [])
        risks = parsed.get("risks", [])
        missing = parsed.get("missing_keywords", [])

        def to_line(value: object) -> str:
            if isinstance(value, list):
                return ", ".join(str(item) for item in value) if value else "None"
            return str(value)

        lines = [
            f"Fit score: {score}",
            f"Strengths: {to_line(strengths)}",
            f"Risks: {to_line(risks)}",
            f"Missing keywords: {to_line(missing)}",
        ]
        return "\n".join(lines)
