from __future__ import annotations

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
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.settings.ollama_base_url}/api/generate",
                json=body,
            )
            response.raise_for_status()
            data = response.json()
        return data.get("response", "").strip()

    async def score_job_fit(self, profile: str, job_description: str) -> str:
        prompt = (
            "You are a strict career assistant. Return concise JSON with keys "
            "fit_score_0_100, strengths, risks, and missing_keywords.\n\n"
            f"Profile:\n{profile}\n\nJob Description:\n{job_description}"
        )
        return await self.generate(prompt, temperature=0.1)

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
