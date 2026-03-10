from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


ExperienceType = Literal["job", "project"]


class Experience(BaseModel):
    id: str
    type: ExperienceType
    title: str
    organization: str
    date_range: str = ""
    summary: str = ""
    bullets: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class ExperienceCreate(BaseModel):
    type: ExperienceType
    title: str
    organization: str
    date_range: str = ""
    summary: str = ""
    bullets: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class ExperienceUpdate(BaseModel):
    type: Optional[ExperienceType] = None
    title: Optional[str] = None
    organization: Optional[str] = None
    date_range: Optional[str] = None
    summary: Optional[str] = None
    bullets: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class RewriteRequest(BaseModel):
    jd: str
    experience_id: str
    rewrite_instruction: str


class RewriteResponse(BaseModel):
    experience_id: str
    original_bullets: List[str]
    rewritten_bullets: List[str]
