from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from src.domain.entities import ExperienceCatalogItem, ExperienceDraft, Session


class JsonStorage:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.experiences_path = data_dir / "experiences.json"
        self.sessions_dir = data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def load_experiences(self) -> List[ExperienceCatalogItem]:
        if not self.experiences_path.exists():
            raise FileNotFoundError(f"Missing experiences file: {self.experiences_path}")
        raw = json.loads(self.experiences_path.read_text())
        return [ExperienceCatalogItem.model_validate(item) for item in raw]

    def create_session(self, job_description: str, selected_ids: List[str]) -> Session:
        now = datetime.now(timezone.utc).isoformat()
        session_id = str(uuid4())
        drafts: Dict[str, ExperienceDraft] = {
            exp_id: ExperienceDraft(experience_id=exp_id) for exp_id in selected_ids
        }
        session = Session(
            session_id=session_id,
            job_description=job_description,
            selected_experience_ids=selected_ids,
            drafts_by_experience=drafts,
            created_at=now,
            updated_at=now,
        )
        self.save_session(session)
        return session

    def save_session(self, session: Session) -> None:
        session.touch()
        path = self.sessions_dir / f"{session.session_id}.json"
        path.write_text(session.model_dump_json(indent=2))

    def load_session(self, session_id: str) -> Session:
        path = self.sessions_dir / f"{session_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        return Session.model_validate_json(path.read_text())
