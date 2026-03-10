from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .llm_service import LlmService
from .models import Experience, ExperienceCreate, ExperienceUpdate, RewriteRequest, RewriteResponse
from .repository import ExperienceRepository

app = FastAPI(title="Resume Workspace API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = ExperienceRepository(Path(__file__).resolve().parent.parent / "data" / "experiences.json")
llm_service = LlmService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/experiences", response_model=list[Experience])
def list_experiences() -> list[Experience]:
    return repo.list()


@app.post("/experiences", response_model=Experience)
def create_experience(payload: ExperienceCreate) -> Experience:
    return repo.create(payload)


@app.patch("/experiences/{experience_id}", response_model=Experience)
def update_experience(experience_id: str, payload: ExperienceUpdate) -> Experience:
    updated = repo.update(experience_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    return updated


@app.delete("/experiences/{experience_id}")
def delete_experience(experience_id: str) -> dict[str, bool]:
    deleted = repo.delete(experience_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Experience not found")
    return {"ok": True}


@app.post("/rewrite", response_model=RewriteResponse)
def rewrite_experience(payload: RewriteRequest) -> RewriteResponse:
    experience = repo.get(payload.experience_id)
    if experience is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    rewritten = llm_service.rewrite_bullets(
        jd=payload.jd,
        experience=experience,
        rewrite_instruction=payload.rewrite_instruction,
    )
    return RewriteResponse(
        experience_id=experience.id,
        original_bullets=experience.bullets,
        rewritten_bullets=rewritten,
    )
