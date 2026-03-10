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
python -m src.cli.main generate \
  --jd "Backend engineer role focused on APIs and Python" \
  --experience-ids "exp_backend_1,exp_data_1" \
  --suggestions-json '{"exp_backend_1":{"keywords":["python","fastapi"],"bullet_count":3},"exp_data_1":{"keywords":["etl","analytics"],"bullet_count":2}}'
```

This one-shot command prints tailored bullets immediately and exits.
For offline demo without Ollama, add `--use-mock-llm`.

If you want a single command that does setup + run:

```bash
./run_prototype.sh
```

The script creates/uses `.venv`, installs requirements, asks for JD/inputs, and runs generation.

## Simple frontend (for testing)

Run:

```bash
./run_frontend.sh
```

This opens a Streamlit UI where you can:
- paste only a JD,
- use stubbed experiences/suggestions,
- generate tailored bullets with one click.

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

The CLI now runs a startup health check and will stop early with guidance if the model server is unreachable or the model is missing.

Optional environment variables:

- `RESUME_TAILOR_LLM_MODEL` (default: `qwen3:4b`)
- `RESUME_TAILOR_OLLAMA_URL` (default: `http://localhost:11434/api/generate`)
- `RESUME_TAILOR_OLLAMA_TIMEOUT_SECONDS` (default: `60`)
