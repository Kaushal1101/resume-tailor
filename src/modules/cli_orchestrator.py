from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from src.domain.entities import ExperienceCatalogItem, ExperienceStatus, Session, SuggestionPayload
from src.modules.review_controller import ReviewController
from src.modules.session_manager import SessionManager
from src.modules.storage import JsonStorage


class CliOrchestrator:
    def __init__(self, data_dir: Path, use_mock_llm: bool = False) -> None:
        self.storage = JsonStorage(data_dir=data_dir)
        self.llm = self._build_llm(use_mock_llm)
        self.session_manager = SessionManager(llm=self.llm)
        self.review_controller = ReviewController(self.session_manager)

    @staticmethod
    def _build_llm(use_mock_llm: bool):
        from src.modules.llm_module import LlmModule

        return LlmModule(use_mock=use_mock_llm)

    def run(self) -> Session:
        self._ensure_llm_ready()

        experiences = self.storage.load_experiences()
        experiences_by_id: Dict[str, ExperienceCatalogItem] = {e.id: e for e in experiences}

        jd = input("Paste Job Description (single line): ").strip()
        selected_ids = self._collect_selected_ids(experiences_by_id)
        suggestions_by_id = self._collect_suggestions(selected_ids)

        session = self.storage.create_session(jd, selected_ids)
        session = self.session_manager.initialize_generation(
            session=session,
            experiences_by_id=experiences_by_id,
            suggestions_by_id=suggestions_by_id,
        )
        self.storage.save_session(session)

        while not session.is_complete:
            self._print_session(session)
            experience_id = input("Choose experience id to review: ").strip()
            action = input("Action [accept/reject/iterate]: ").strip().lower()
            if action not in {"accept", "reject", "iterate"}:
                print("Invalid action, try again.")
                continue
            action_suggestions = (
                suggestions_by_id.get(experience_id, SuggestionPayload())
                if action == "accept"
                else self._collect_suggestions([experience_id]).get(experience_id, SuggestionPayload())
            )
            session = self.review_controller.handle_action(
                session=session,
                experience_id=experience_id,
                action=action,
                suggestions=action_suggestions,
                experiences_by_id=experiences_by_id,
            )
            self.storage.save_session(session)

        print("All experiences accepted. Session complete.")
        self._print_session(session)
        return session

    def generate_once(
        self,
        job_description: str,
        selected_ids: List[str],
        suggestions_by_id: Dict[str, SuggestionPayload] | None = None,
    ) -> Session:
        """Generate tailored bullets once and return session snapshot."""
        self._ensure_llm_ready()
        experiences = self.storage.load_experiences()
        experiences_by_id: Dict[str, ExperienceCatalogItem] = {e.id: e for e in experiences}
        for exp_id in selected_ids:
            if exp_id not in experiences_by_id:
                raise ValueError(f"Unknown experience id: {exp_id}")

        session = self.storage.create_session(job_description, selected_ids)
        session = self.session_manager.initialize_generation(
            session=session,
            experiences_by_id=experiences_by_id,
            suggestions_by_id=suggestions_by_id or {},
        )
        self.storage.save_session(session)
        self._print_session(session)
        return session

    @staticmethod
    def _collect_selected_ids(experiences_by_id: Dict[str, ExperienceCatalogItem]) -> List[str]:
        print("\nAvailable experiences:")
        for exp_id, exp in experiences_by_id.items():
            print(f"- {exp_id}: {exp.title} @ {exp.company}")
        selected = input("Enter comma-separated experience ids: ").strip()
        selected_ids = [item.strip() for item in selected.split(",") if item.strip()]
        for exp_id in selected_ids:
            if exp_id not in experiences_by_id:
                raise ValueError(f"Unknown experience id: {exp_id}")
        return selected_ids

    @staticmethod
    def _collect_suggestions(experience_ids: List[str]) -> Dict[str, SuggestionPayload]:
        suggestions_map: Dict[str, SuggestionPayload] = {}
        for exp_id in experience_ids:
            raw = input(
                f"Suggestions for {exp_id} as JSON "
                "(or empty for defaults): "
            ).strip()
            if not raw:
                suggestions_map[exp_id] = SuggestionPayload()
                continue
            suggestions_map[exp_id] = SuggestionPayload.model_validate(json.loads(raw))
        return suggestions_map

    @staticmethod
    def _print_session(session: Session) -> None:
        print("\nCurrent session state:")
        for exp_id in session.selected_experience_ids:
            draft = session.drafts_by_experience[exp_id]
            print(
                f"[{exp_id}] status={draft.status.value} iteration={draft.iteration} "
                f"bullets={len(draft.bullets_current)}"
            )
            for idx, bullet in enumerate(draft.bullets_current, start=1):
                print(f"  {idx}. {bullet}")
        remaining = [
            exp_id
            for exp_id, draft in session.drafts_by_experience.items()
            if draft.status != ExperienceStatus.accepted
        ]
        print(f"Remaining to accept: {remaining}\n")

    def _ensure_llm_ready(self) -> None:
        healthy, message = self.llm.health_check()
        if not healthy:
            raise RuntimeError(f"LLM health check failed: {message}")
        print(f"LLM ready: {message}")
