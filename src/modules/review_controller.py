from __future__ import annotations

from typing import Dict

from src.domain.entities import ExperienceCatalogItem, Session, SuggestionPayload
from src.modules.session_manager import SessionManager


class ReviewController:
    def __init__(self, session_manager: SessionManager) -> None:
        self.session_manager = session_manager

    def handle_action(
        self,
        session: Session,
        experience_id: str,
        action: str,
        suggestions: SuggestionPayload,
        experiences_by_id: Dict[str, ExperienceCatalogItem],
    ) -> Session:
        if action == "accept":
            return self.session_manager.accept(session, experience_id)
        if action == "reject":
            return self.session_manager.reject(
                session, experience_id, experiences_by_id[experience_id], suggestions
            )
        if action == "iterate":
            return self.session_manager.iterate(
                session, experience_id, experiences_by_id[experience_id], suggestions
            )
        raise ValueError(f"Unsupported action: {action}")
