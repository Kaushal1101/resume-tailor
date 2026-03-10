from __future__ import annotations

from typing import List

from src.domain.entities import ExperienceCatalogItem, SuggestionPayload


class LlmModule:
    """Stubbed LLM service for local prototyping."""

    def generate_from_scratch(
        self,
        job_description: str,
        experience: ExperienceCatalogItem,
        suggestions: SuggestionPayload,
    ) -> List[str]:
        count = max(1, suggestions.bullet_count)
        keyphrase = ", ".join(suggestions.keywords[:3]) if suggestions.keywords else "core impact"
        return [
            f"Led {experience.title} initiatives at {experience.company}, aligning outcomes with JD focus on {keyphrase}."
            for _ in range(count)
        ]

    def refine_existing(
        self,
        job_description: str,
        experience: ExperienceCatalogItem,
        suggestions: SuggestionPayload,
        current_bullets: List[str],
    ) -> List[str]:
        if not current_bullets:
            return self.generate_from_scratch(job_description, experience, suggestions)
        tool_hint = suggestions.tools[0] if suggestions.tools else "relevant tooling"
        return [f"{bullet} Emphasized {tool_hint} and measurable execution." for bullet in current_bullets]
