# Resume Tailor (CLI Prototype)

CLI-first resume tailoring prototype with per-experience review loops.

## What it does

- Takes a Job Description (JD) as input.
- Loads selected experiences from `data/experiences.json`.
- Accepts per-experience suggestions (`keywords`, `tools`, `skills`, `bullet_count`, plus extensible `extra` fields).
- Generates bullets independently per experience.
- Supports per-experience actions:
  - `accept`: lock bullets for one experience.
  - `reject`: regenerate that experience from scratch with new suggestions.
  - `iterate`: refine existing bullets for that experience.
- Loops until all selected experiences are accepted.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.cli.main run
```

## Notes

- This prototype uses local JSON persistence under `data/sessions`.
- LLM generation uses a local Ollama endpoint by default with model `qwen3:4b`.

## Local model setup (Ollama)

1. Install and run Ollama locally.
2. Pull the model:

```bash
ollama pull qwen3:4b
```

3. Start Ollama server (if not already running):

```bash
ollama serve
```

Optional environment variables:

- `RESUME_TAILOR_LLM_MODEL` (default: `qwen3:4b`)
- `RESUME_TAILOR_OLLAMA_URL` (default: `http://localhost:11434/api/generate`)
- `RESUME_TAILOR_OLLAMA_TIMEOUT_SECONDS` (default: `60`)
