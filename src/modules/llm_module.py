from __future__ import annotations

import json
import os
from pathlib import Path
from urllib import error, request
from typing import Any, Dict, List

from src.domain.entities import ExperienceCatalogItem, SuggestionPayload


class LlmModule:
    """LLM adapter with strict JSON output parsing and retry fallback."""

    def __init__(self, use_mock: bool = False) -> None:
        base_dir = Path(__file__).resolve().parent.parent
        self._generate_template = (base_dir / "templates" / "prompt_generate.txt").read_text()
        self._refine_template = (base_dir / "templates" / "prompt_refine.txt").read_text()
        self.model_name = os.getenv("RESUME_TAILOR_LLM_MODEL", "qwen3:4b")
        self.base_url = os.getenv("RESUME_TAILOR_OLLAMA_URL", "http://localhost:11434/api/generate")
        self.timeout_seconds = float(os.getenv("RESUME_TAILOR_OLLAMA_TIMEOUT_SECONDS", "60"))
        self.use_mock = use_mock

    def generate_from_scratch(
        self,
        job_description: str,
        experience: ExperienceCatalogItem,
        suggestions: SuggestionPayload,
    ) -> List[str]:
        prompt = self._generate_template.format(
            job_description=job_description,
            experience_json=json.dumps(experience.model_dump(), indent=2),
            suggestions_json=json.dumps(suggestions.model_dump(), indent=2),
        )
        raw = self._call_model(prompt=prompt, mode="generate")
        bullets = self._parse_bullets(raw)
        if bullets:
            return bullets
        retry_raw = self._call_model(prompt=f"{prompt}\n\nSTRICT_JSON", mode="generate")
        retry_bullets = self._parse_bullets(retry_raw)
        if retry_bullets:
            return retry_bullets
        return self._fallback_bullets(experience, suggestions)

    def refine_existing(
        self,
        job_description: str,
        experience: ExperienceCatalogItem,
        suggestions: SuggestionPayload,
        current_bullets: List[str],
    ) -> List[str]:
        if not current_bullets:
            return self.generate_from_scratch(job_description, experience, suggestions)
        prompt = self._refine_template.format(
            job_description=job_description,
            experience_json=json.dumps(experience.model_dump(), indent=2),
            current_bullets_json=json.dumps(current_bullets, indent=2),
            suggestions_json=json.dumps(suggestions.model_dump(), indent=2),
        )
        raw = self._call_model(prompt=prompt, mode="refine")
        bullets = self._parse_bullets(raw)
        if bullets:
            return bullets
        retry_raw = self._call_model(prompt=f"{prompt}\n\nSTRICT_JSON", mode="refine")
        retry_bullets = self._parse_bullets(retry_raw)
        if retry_bullets:
            return retry_bullets
        tool_hint = suggestions.tools[0] if suggestions.tools else "relevant tooling"
        return [f"{bullet} Emphasized {tool_hint} and measurable execution." for bullet in current_bullets]

    @staticmethod
    def _parse_bullets(raw_output: str) -> List[str]:
        try:
            parsed: Dict[str, Any] = json.loads(raw_output)
            bullets = parsed.get("bullets", [])
            if not isinstance(bullets, list):
                return []
            cleaned = [str(item).strip() for item in bullets if str(item).strip()]
            return cleaned
        except json.JSONDecodeError:
            return []

    def _call_model(self, prompt: str, mode: str) -> str:
        """Call local Ollama model and return raw text content."""
        if self.use_mock:
            if "STRICT_JSON" in prompt:
                bullets = [
                    f"{mode.title()} bullet aligned to JD and targeted experience.",
                    f"{mode.title()} bullet emphasizing measurable impact and role fit.",
                ]
                return json.dumps({"bullets": bullets})
            return "- malformed bullet line one\n- malformed bullet line two"

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
                # Ollama response format includes a plain text field named "response".
                return str(decoded.get("response", ""))
        except (error.URLError, TimeoutError, json.JSONDecodeError):
            return ""

    @staticmethod
    def _fallback_bullets(
        experience: ExperienceCatalogItem,
        suggestions: SuggestionPayload,
    ) -> List[str]:
        count = max(1, suggestions.bullet_count)
        keyphrase = ", ".join(suggestions.keywords[:3]) if suggestions.keywords else "core impact"
        return [
            f"Led {experience.title} initiatives at {experience.company}, aligned with {keyphrase}."
            for _ in range(count)
        ]
