import pytest

from src.domain.entities import ExperienceCatalogItem, ExperienceStatus, Session, SuggestionPayload
from src.modules.llm_module import LlmModule
from src.modules.review_controller import ReviewController
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


def build_experiences():
    return {
        "exp1": ExperienceCatalogItem(id="exp1", title="SE", company="A"),
        "exp2": ExperienceCatalogItem(id="exp2", title="DE", company="B"),
    }


def test_iterate_is_isolated_to_single_experience() -> None:
    manager = SessionManager(LlmModule())
    session = build_session()
    experiences = build_experiences()
    manager.initialize_generation(session, experiences, {})
    exp2_before = list(session.drafts_by_experience["exp2"].bullets_current)

    manager.iterate(
        session=session,
        experience_id="exp1",
        experience=experiences["exp1"],
        additional_suggestions=SuggestionPayload(tools=["FastAPI"]),
    )

    assert session.drafts_by_experience["exp2"].bullets_current == exp2_before


def test_session_completes_only_when_all_experiences_accepted() -> None:
    manager = SessionManager(LlmModule())
    session = build_session()
    experiences = build_experiences()
    manager.initialize_generation(session, experiences, {})

    assert session.is_complete is False
    manager.accept(session, "exp1")
    assert session.is_complete is False
    manager.accept(session, "exp2")
    assert session.is_complete is True


def test_review_controller_rejects_unknown_action() -> None:
    manager = SessionManager(LlmModule())
    controller = ReviewController(manager)
    session = build_session()
    experiences = build_experiences()
    manager.initialize_generation(session, experiences, {})

    with pytest.raises(ValueError):
        controller.handle_action(
            session=session,
            experience_id="exp1",
            action="unknown",
            suggestions=SuggestionPayload(),
            experiences_by_id=experiences,
        )


def test_accept_locks_specific_experience_only() -> None:
    manager = SessionManager(LlmModule())
    session = build_session()
    experiences = build_experiences()
    manager.initialize_generation(session, experiences, {})
    manager.accept(session, "exp1")

    assert session.drafts_by_experience["exp1"].status == ExperienceStatus.accepted
    assert session.drafts_by_experience["exp2"].status == ExperienceStatus.drafted
