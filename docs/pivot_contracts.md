# Resume Workspace Pivot Contracts

## Folder Structure

```text
backend/
  app/
    main.py
    models.py
    repository.py
    llm_service.py
  data/
    experiences.json
  tests/
    test_api.py
  requirements.txt
frontend/
  package.json
  index.html
  src/
    main.jsx
    App.jsx
```

## Experience JSON Schema

- `id`: string, unique key
- `type`: `"job"` or `"project"`
- `title`: string
- `organization`: string
- `date_range`: string
- `summary`: string
- `bullets`: string[]
- `tags`: string[]

## API Contracts

### `GET /experiences`
- Returns full list of experiences.

### `POST /experiences`
- Creates new experience.
- Body: experience fields without `id`.
- Returns created experience with generated `id`.

### `PATCH /experiences/{experience_id}`
- Partial update for one experience.
- Returns updated record.

### `DELETE /experiences/{experience_id}`
- Deletes one experience.
- Returns `{ "ok": true }`.

### `POST /rewrite`
- Rewrites bullets only for selected experience.
- Body:
  - `jd`: string
  - `experience_id`: string
  - `rewrite_instruction`: string
- Returns:
  - `experience_id`
  - `original_bullets`
  - `rewritten_bullets`

## Cleanup Map

Remove legacy files from old flow:
- `src/` package and old modules
- `tests/` legacy CLI/session tests
- `frontend_app.py`
- `run_prototype.sh`

Keep and repurpose:
- `run_frontend.sh` (replace with React launcher)
- Ollama integration approach from old `llm_module` (moved to backend service)

## MVP Definition of Done

- User can view stored experiences in a scrollable UI list.
- User can paste JD and provide rewrite instruction.
- User can click one experience and rewrite only that selected experience.
- User sees rewritten bullets in UI.
- Experiences persist in JSON.
