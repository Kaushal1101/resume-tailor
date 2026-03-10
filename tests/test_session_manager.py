from src.domain.entities import ExperienceCatalogItem, ExperienceStatus, Session, SuggestionPayload
from src.modules.llm_module import LlmModule
from src.modules.session_manager import SessionManager


def build_session() -> Session:
    return Session.model_validate(
        {
            "session_id": "s1",
            "job_description": "Backend engineer role",
            "selected_experience_ids": ["exp1", "exp2"],
            "drafts_by_experience": {
                "exp1": {"experience_id": "exp1"},
                "exp2": {"experience_id": "exp2"},
            },
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
        }
    )


def test_reject_is_isolated_to_target_experience() -> None:
    manager = SessionManager(LlmModule(use_mock=True))
    session = build_session()
    experiences = {
        "exp1": ExperienceCatalogItem(id="exp1", title="SE", company="A"),
        "exp2": ExperienceCatalogItem(id="exp2", title="DE", company="B"),
    }
    manager.initialize_generation(session, experiences, {})
    exp2_before = list(session.drafts_by_experience["exp2"].bullets_current)

    manager.reject(
        session=session,
        experience_id="exp1",
        experience=experiences["exp1"],
        new_suggestions=SuggestionPayload(keywords=["python"], bullet_count=2),
    )

    assert session.drafts_by_experience["exp2"].bullets_current == exp2_before


def test_accepted_experience_is_locked() -> None:
    manager = SessionManager(LlmModule(use_mock=True))
    session = build_session()
    experiences = {
        "exp1": ExperienceCatalogItem(id="exp1", title="SE", company="A"),
        "exp2": ExperienceCatalogItem(id="exp2", title="DE", company="B"),
    }
    manager.initialize_generation(session, experiences, {})
    manager.accept(session, "exp1")

    assert session.drafts_by_experience["exp1"].status == ExperienceStatus.accepted

    try:
        manager.iterate(
            session=session,
            experience_id="exp1",
            experience=experiences["exp1"],
            additional_suggestions=SuggestionPayload(tools=["FastAPI"]),
        )
        raise AssertionError("Expected locked experience iteration to fail.")
    except ValueError as exc:
        assert "locked" in str(exc)
