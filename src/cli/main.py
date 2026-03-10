from __future__ import annotations

import json
from pathlib import Path

import typer

from src.domain.entities import SuggestionPayload
from src.modules.cli_orchestrator import CliOrchestrator

app = typer.Typer(help="Resume Tailoring CLI")


@app.command()
def run(
    data_dir: str = "data",
    use_mock_llm: bool = typer.Option(False, help="Use mock LLM instead of local Ollama."),
) -> None:
    """Run the interactive resume tailoring workflow."""
    orchestrator = CliOrchestrator(data_dir=Path(data_dir), use_mock_llm=use_mock_llm)
    orchestrator.run()


@app.command()
def generate(
    jd: str = typer.Option(..., help="Job description text."),
    experience_ids: str = typer.Option(
        ..., help="Comma-separated experience ids (example: exp_backend_1,exp_data_1)."
    ),
    suggestions_json: str = typer.Option(
        "{}", help="Optional JSON object keyed by experience id for suggestions."
    ),
    data_dir: str = typer.Option("data", help="Data directory containing experiences.json."),
    use_mock_llm: bool = typer.Option(False, help="Use mock LLM instead of local Ollama."),
) -> None:
    """One-shot generation: print tailored bullets and exit."""
    orchestrator = CliOrchestrator(data_dir=Path(data_dir), use_mock_llm=use_mock_llm)
    selected_ids = [item.strip() for item in experience_ids.split(",") if item.strip()]
    raw_suggestions = json.loads(suggestions_json)
    suggestions_by_id = {
        key: SuggestionPayload.model_validate(value) for key, value in raw_suggestions.items()
    }
    orchestrator.generate_once(
        job_description=jd,
        selected_ids=selected_ids,
        suggestions_by_id=suggestions_by_id,
    )


if __name__ == "__main__":
    app()
