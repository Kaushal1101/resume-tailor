import json

from src.domain.entities import SuggestionPayload
from src.modules.cli_orchestrator import CliOrchestrator


def test_generate_once_creates_bullets_and_session(tmp_path) -> None:
    data_dir = tmp_path / "data"
    sessions_dir = data_dir / "sessions"
    sessions_dir.mkdir(parents=True)
    experiences_path = data_dir / "experiences.json"
    experiences_path.write_text(
        json.dumps(
            [
                {
                    "id": "exp_backend_1",
                    "title": "Software Engineer",
                    "company": "Acme Corp",
                    "metadata": {},
                    "base_bullets": [],
                }
            ]
        )
    )

    orchestrator = CliOrchestrator(data_dir=data_dir, use_mock_llm=True)
    session = orchestrator.generate_once(
        job_description="Backend role",
        selected_ids=["exp_backend_1"],
        suggestions_by_id={
            "exp_backend_1": SuggestionPayload(keywords=["python"], bullet_count=2),
        },
    )

    draft = session.drafts_by_experience["exp_backend_1"]
    assert len(draft.bullets_current) >= 1
    assert draft.iteration == 1
