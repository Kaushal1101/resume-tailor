# Resume Tailoring Prototype Architecture (Phase 0)

## System overview

The application takes a job description (JD), loads selected experiences from a JSON store, accepts per-experience suggestion payloads, and uses an LLM to generate tailored bullets independently for each experience.

Users can then review each experience and choose one action:
- Accept: lock bullets for that experience.
- Reject: regenerate from scratch with new suggestions.
- Iterate: refine existing bullets with additional suggestions.

The process loops until all selected experiences are accepted.

## Architecture choice

CLI-first architecture is recommended for the prototype:
- fastest path to a working workflow,
- explicit state transitions for debugging,
- easy extension to API/UI later without redesigning core logic.

## Domain model

- `ExperienceCatalogItem`
  - `id`, `title`, `company`, optional metadata, baseline bullets.
- `SuggestionPayload`
  - `keywords`, `tools`, `skills`, `bullet_count`, `extra` (extensible dict).
- `ExperienceDraft`
  - `experience_id`, `status`, `bullets_current`, `suggestions_current`, `iteration`, `history`.
- `Session`
  - `session_id`, `job_description`, `selected_experience_ids`, `drafts_by_experience`, timestamps.

## Per-experience state machine

States:
- `pending`: selected but not yet generated.
- `drafted`: generated and reviewable.
- `accepted`: locked and immutable.

Transitions:
- `pending -> drafted` (initial generation),
- `drafted -> drafted` (reject or iterate),
- `drafted -> accepted` (accept),
- `accepted -> accepted` (immutable in prototype).

Invariants:
- Mutations are scoped to a single `experience_id`.
- Regenerating one experience must never overwrite others.
- Accepted drafts are immutable.
- Session completes only when all drafts are accepted.

## Module boundaries

- `storage`
  - Loads experiences and persists session snapshots.
- `session_manager`
  - Enforces state transitions, invariants, and completion logic.
- `llm_module`
  - Performs `generate_from_scratch` and `refine_existing` for one experience at a time.
- `review_controller`
  - Maps user action (accept/reject/iterate) to session + LLM operations.
- `cli_orchestrator`
  - Coordinates the end-to-end interaction loop.

## Risks and mitigations

1. Cross-experience overwrite bugs
   - Mitigate with id-scoped updates and isolation tests.
2. Reject vs iterate ambiguity
   - Mitigate with explicit action mode and separate LLM methods.
3. Session loss on interruption
   - Mitigate by saving session after every action.
4. Unreliable LLM outputs
   - Mitigate with output validation and prompt constraints.
5. Scope creep
   - Keep prototype local and CLI-only before frontend/API work.

## Definition of done (Phase 0)

- Architecture and contracts documented.
- Per-experience state machine and invariants defined.
- Module responsibilities and boundaries are clear.
- Implementation can proceed without unresolved design ambiguity.
