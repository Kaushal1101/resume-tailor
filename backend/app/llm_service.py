from __future__ import annotations

import json
import os
from urllib import error, request

from .models import Experience


class LlmService:
    def __init__(self) -> None:
        self.model_name = os.getenv("RESUME_TAILOR_LLM_MODEL", "qwen3:4b")
        self.base_url = os.getenv("RESUME_TAILOR_OLLAMA_URL", "http://localhost:11434/api/generate")
        self.timeout_seconds = float(os.getenv("RESUME_TAILOR_OLLAMA_TIMEOUT_SECONDS", "60"))
        self.use_mock = os.getenv("RESUME_TAILOR_USE_MOCK_LLM", "false").lower() == "true"

    def rewrite_bullets(
        self,
        jd: str,
        experience: Experience,
        rewrite_instruction: str,
    ) -> list[str]:
        prompt = self._build_prompt(jd=jd, experience=experience, rewrite_instruction=rewrite_instruction)
        raw = self._call_model(prompt)
        parsed = self._parse(raw)
        if parsed:
            return parsed
        retry_raw = self._call_model(prompt + "\n\nSTRICT_JSON")
        retry_parsed = self._parse(retry_raw)
        if retry_parsed:
            return retry_parsed
        return self._fallback(experience.bullets, rewrite_instruction)

    def _call_model(self, prompt: str) -> str:
        if self.use_mock:
            return json.dumps(
                {
                    "rewritten_bullets": [
                        "Mock rewrite bullet tailored for selected experience.",
                        "Mock rewrite bullet emphasizing JD relevance.",
                    ]
                }
            )
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        req = request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                decoded = json.loads(response.read().decode("utf-8"))
                return str(decoded.get("response", ""))
        except (error.URLError, TimeoutError, json.JSONDecodeError):
            return ""

    @staticmethod
    def _parse(raw_output: str) -> list[str]:
        try:
            data = json.loads(raw_output)
            bullets = data.get("rewritten_bullets", [])
            if not isinstance(bullets, list):
                return []
            return [str(item).strip() for item in bullets if str(item).strip()]
        except json.JSONDecodeError:
            return []

    @staticmethod
    def _fallback(original_bullets: list[str], instruction: str) -> list[str]:
        if not original_bullets:
            return [f"Rewrite unavailable. Instruction noted: {instruction}"]
        return [f"{bullet} ({instruction})" for bullet in original_bullets]

    @staticmethod
    def _build_prompt(jd: str, experience: Experience, rewrite_instruction: str) -> str:
        return f"""
You are rewriting resume bullets for exactly one selected experience.
Return strict JSON only: {{"rewritten_bullets": ["...", "..."]}}

Job Description:
{jd}

Selected Experience:
{json.dumps(experience.model_dump(), indent=2)}

Rewrite Instruction:
{rewrite_instruction}
""".strip()
