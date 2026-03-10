from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ExperienceStatus(str, Enum):
    pending = "pending"
    drafted = "drafted"
    accepted = "accepted"


class ExperienceCatalogItem(BaseModel):
    id: str
    title: str
    company: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    base_bullets: List[str] = Field(default_factory=list)


class SuggestionPayload(BaseModel):
    keywords: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    bullet_count: int = 3
    extra: Dict[str, Any] = Field(default_factory=dict)


class DraftHistoryEntry(BaseModel):
    action: str
    timestamp: str
    suggestions: SuggestionPayload
    bullets: List[str]


class ExperienceDraft(BaseModel):
    experience_id: str
    status: ExperienceStatus = ExperienceStatus.pending
    suggestions_current: SuggestionPayload = Field(default_factory=SuggestionPayload)
    bullets_current: List[str] = Field(default_factory=list)
    iteration: int = 0
    history: List[DraftHistoryEntry] = Field(default_factory=list)


class Session(BaseModel):
    session_id: str
    job_description: str
    selected_experience_ids: List[str]
    drafts_by_experience: Dict[str, ExperienceDraft]
    created_at: str
    updated_at: str

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    @property
    def is_complete(self) -> bool:
        return all(
            self.drafts_by_experience[eid].status == ExperienceStatus.accepted
            for eid in self.selected_experience_ids
        )
