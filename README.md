# Resume Workspace (React + FastAPI)

Web app for rewriting resume bullets experience-by-experience.

## What this app does

- Stores resume experiences in JSON (`backend/data/experiences.json`).
- Shows a scrollable experience list in the frontend.
- Lets you paste a JD and write a short rewrite instruction.
- Rewrites bullets only for the selected experience via local LLM (`qwen3:4b` on Ollama).

## Run locally

Open two terminals from repo root:

1) Start backend:

```bash
./run_backend.sh
```

2) Start frontend:

```bash
./run_frontend.sh
```

Frontend URL: `http://localhost:5173`
Backend URL: `http://localhost:8000`

## Local model setup (Ollama)

```bash
ollama pull qwen3:4b
ollama serve
```

Optional environment variables:

- `RESUME_TAILOR_LLM_MODEL` (default: `qwen3:4b`)
- `RESUME_TAILOR_OLLAMA_URL` (default: `http://localhost:11434/api/generate`)
- `RESUME_TAILOR_OLLAMA_TIMEOUT_SECONDS` (default: `60`)
- `RESUME_TAILOR_USE_MOCK_LLM` (`true` to bypass Ollama for testing)

## API Summary

- `GET /experiences`
- `POST /experiences`
- `PATCH /experiences/{experience_id}`
- `DELETE /experiences/{experience_id}`
- `POST /rewrite`
