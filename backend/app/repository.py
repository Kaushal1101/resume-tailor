from __future__ import annotations

import json
from pathlib import Path
from typing import List
from uuid import uuid4

from .models import Experience, ExperienceCreate, ExperienceUpdate


class ExperienceRepository:
    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_path.exists():
            self.data_path.write_text("[]")

    def list(self) -> List[Experience]:
        raw = json.loads(self.data_path.read_text())
        return [Experience.model_validate(item) for item in raw]

    def get(self, experience_id: str) -> Experience | None:
        for item in self.list():
            if item.id == experience_id:
                return item
        return None

    def create(self, payload: ExperienceCreate) -> Experience:
        items = self.list()
        created = Experience(id=str(uuid4()), **payload.model_dump())
        items.append(created)
        self._save(items)
        return created

    def update(self, experience_id: str, payload: ExperienceUpdate) -> Experience | None:
        items = self.list()
        updated: Experience | None = None
        for index, item in enumerate(items):
            if item.id != experience_id:
                continue
            merged = item.model_dump()
            for key, value in payload.model_dump(exclude_unset=True).items():
                merged[key] = value
            updated = Experience.model_validate(merged)
            items[index] = updated
            break
        if updated is None:
            return None
        self._save(items)
        return updated

    def delete(self, experience_id: str) -> bool:
        items = self.list()
        next_items = [item for item in items if item.id != experience_id]
        if len(next_items) == len(items):
            return False
        self._save(next_items)
        return True

    def _save(self, items: List[Experience]) -> None:
        self.data_path.write_text(json.dumps([item.model_dump() for item in items], indent=2))
