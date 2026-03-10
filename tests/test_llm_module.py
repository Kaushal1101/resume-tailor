from src.domain.entities import ExperienceCatalogItem, SuggestionPayload
from src.modules.llm_module import LlmModule


def test_generate_retries_and_returns_structured_bullets() -> None:
    llm = LlmModule(use_mock=True)
    bullets = llm.generate_from_scratch(
        job_description="Build backend APIs",
        experience=ExperienceCatalogItem(id="exp1", title="Software Engineer", company="Acme"),
        suggestions=SuggestionPayload(keywords=["python"], bullet_count=2),
    )
    assert len(bullets) >= 1
    assert all(isinstance(item, str) and item for item in bullets)


def test_parse_bullets_rejects_non_json_output() -> None:
    parsed = LlmModule._parse_bullets("not-json")
    assert parsed == []
