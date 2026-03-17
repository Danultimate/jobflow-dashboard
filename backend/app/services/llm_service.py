from __future__ import annotations

import json
import re

import httpx

from app.core.config import get_settings


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate(
        self, prompt: str, temperature: float = 0.2, max_tokens: int | None = None
    ) -> str:
        options: dict[str, float | int] = {"temperature": temperature}
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        body = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30m",
            "options": options,
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
        raw = await self.generate(prompt, temperature=0.1, max_tokens=220)
        return self._format_fit_score_response(raw)

    async def draft_cover_letter(
        self, profile: str, company: str, role: str, job_description: str
    ) -> str:
        prompt = (
            "Write a concise tailored cover letter in plain text only (no markdown/code fences).\n"
            "Limit to 250-320 words, 3 short paragraphs, concrete achievements, no fluff.\n"
            f"Company: {company}\nRole: {role}\n\nProfile:\n{profile}\n\n"
            f"Job Description:\n{job_description}"
        )
        raw = await self.generate(prompt, temperature=0.3, max_tokens=420)
        return self._sanitize_text_output(raw)

    async def review_application(self, resume_text: str, cover_letter: str, job_description: str) -> str:
        prompt = (
            "Review this application package. Return: strengths, red_flags, "
            "improvement_actions, and final_recommendation.\n\n"
            f"Resume:\n{resume_text}\n\nCover Letter:\n{cover_letter}\n\n"
            f"Job Description:\n{job_description}"
        )
        return await self.generate(prompt, temperature=0.1, max_tokens=450)

    def _sanitize_text_output(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned).strip()
        return cleaned

    def _format_fit_score_response(self, response: str) -> str:
        cleaned = self._sanitize_text_output(response)
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
