from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["RESUME_TAILOR_USE_MOCK_LLM"] = "true"

import app.main as main_module  # noqa: E402
from app.repository import ExperienceRepository  # noqa: E402


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    temp_data = tmp_path / "experiences.json"
    temp_data.write_text(
        """[
  {
    "id": "exp_job_backend",
    "type": "job",
    "title": "Software Engineer",
    "organization": "Acme Corp",
    "date_range": "2022-2025",
    "summary": "Built backend services.",
    "bullets": ["Built APIs", "Collaborated with product"],
    "tags": ["python", "backend"]
  }
]"""
    )
    main_module.repo = ExperienceRepository(temp_data)
    return TestClient(main_module.app)


def test_list_experiences(client: TestClient) -> None:
    response = client.get("/experiences")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1


def test_rewrite_selected_experience_only(client: TestClient) -> None:
    items_before = client.get("/experiences").json()
    target_id = items_before[0]["id"]

    response = client.post(
        "/rewrite",
        json={
            "jd": "Need backend API ownership and Python.",
            "experience_id": target_id,
            "rewrite_instruction": "Make bullets impact-focused and concise.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["experience_id"] == target_id
    assert len(payload["rewritten_bullets"]) >= 1


def test_create_experience(client: TestClient) -> None:
    response = client.post(
        "/experiences",
        json={
            "type": "project",
            "title": "Test Experience",
            "organization": "QA Org",
            "date_range": "2026",
            "summary": "Summary",
            "bullets": ["Did a thing"],
            "tags": ["test"],
        },
    )
    assert response.status_code == 200
    created = response.json()
    assert created["id"]
    assert created["title"] == "Test Experience"


def test_repository_file_exists() -> None:
    assert Path(main_module.repo.data_path).exists()
