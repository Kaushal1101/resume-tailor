from __future__ import annotations

from pathlib import Path

import typer

from src.modules.cli_orchestrator import CliOrchestrator

app = typer.Typer(help="Resume Tailoring CLI")


@app.command()
def run(data_dir: str = "data") -> None:
    """Run the interactive resume tailoring workflow."""
    orchestrator = CliOrchestrator(data_dir=Path(data_dir))
    orchestrator.run()


if __name__ == "__main__":
    app()
