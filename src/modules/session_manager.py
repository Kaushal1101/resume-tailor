from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from src.domain.entities import (
    DraftHistoryEntry,
    ExperienceCatalogItem,
    ExperienceStatus,
    Session,
    SuggestionPayload,
)
from src.modules.llm_module import LlmModule


class SessionManager:
    def __init__(self, llm: LlmModule) -> None:
        self.llm = llm

    def initialize_generation(
        self,
        session: Session,
        experiences_by_id: Dict[str, ExperienceCatalogItem],
        suggestions_by_id: Dict[str, SuggestionPayload],
    ) -> Session:
        for experience_id in session.selected_experience_ids:
            suggestions = suggestions_by_id.get(experience_id, SuggestionPayload())
            draft = session.drafts_by_experience[experience_id]
            bullets = self.llm.generate_from_scratch(
                session.job_description,
                experiences_by_id[experience_id],
                suggestions,
            )
            draft.suggestions_current = suggestions
            draft.bullets_current = bullets
            draft.status = ExperienceStatus.drafted
            draft.iteration = 1
            draft.history.append(
                DraftHistoryEntry(
                    action="initial_generate",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    suggestions=suggestions,
                    bullets=bullets,
                )
            )
        session.touch()
        return session

    def accept(self, session: Session, experience_id: str) -> Session:
        draft = self._get_draft(session, experience_id)
        draft.status = ExperienceStatus.accepted
        draft.history.append(
            DraftHistoryEntry(
                action="accept",
                timestamp=datetime.now(timezone.utc).isoformat(),
                suggestions=draft.suggestions_current,
                bullets=draft.bullets_current,
            )
        )
        session.touch()
        return session

    def reject(
        self,
        session: Session,
        experience_id: str,
        experience: ExperienceCatalogItem,
        new_suggestions: SuggestionPayload,
    ) -> Session:
        draft = self._get_draft(session, experience_id)
        self._ensure_not_accepted(draft.status, experience_id)
        bullets = self.llm.generate_from_scratch(
            session.job_description,
            experience,
            new_suggestions,
        )
        draft.suggestions_current = new_suggestions
        draft.bullets_current = bullets
        draft.status = ExperienceStatus.drafted
        draft.iteration += 1
        draft.history.append(
            DraftHistoryEntry(
                action="reject_regenerate",
                timestamp=datetime.now(timezone.utc).isoformat(),
                suggestions=new_suggestions,
                bullets=bullets,
            )
        )
        session.touch()
        return session

    def iterate(
        self,
        session: Session,
        experience_id: str,
        experience: ExperienceCatalogItem,
        additional_suggestions: SuggestionPayload,
    ) -> Session:
        draft = self._get_draft(session, experience_id)
        self._ensure_not_accepted(draft.status, experience_id)
        bullets = self.llm.refine_existing(
            session.job_description,
            experience,
            additional_suggestions,
            draft.bullets_current,
        )
        draft.suggestions_current = additional_suggestions
        draft.bullets_current = bullets
        draft.status = ExperienceStatus.drafted
        draft.iteration += 1
        draft.history.append(
            DraftHistoryEntry(
                action="iterate_refine",
                timestamp=datetime.now(timezone.utc).isoformat(),
                suggestions=additional_suggestions,
                bullets=bullets,
            )
        )
        session.touch()
        return session

    def _get_draft(self, session: Session, experience_id: str):
        if experience_id not in session.drafts_by_experience:
            raise ValueError(f"Experience not in session: {experience_id}")
        return session.drafts_by_experience[experience_id]

    @staticmethod
    def _ensure_not_accepted(status: ExperienceStatus, experience_id: str) -> None:
        if status == ExperienceStatus.accepted:
            raise ValueError(f"Experience already accepted and locked: {experience_id}")
