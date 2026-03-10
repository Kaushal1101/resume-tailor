from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.domain.entities import SuggestionPayload
from src.modules.cli_orchestrator import CliOrchestrator
from src.modules.storage import JsonStorage


st.set_page_config(page_title="Resume Tailor Prototype", layout="wide")
st.title("Resume Tailor Prototype")
st.caption("Simple UI for testing JD -> tailored bullets generation.")

data_dir = st.text_input("Data directory", value="data")
use_mock_llm = st.checkbox("Use mock LLM (skip Ollama)", value=False)

storage = JsonStorage(Path(data_dir))

try:
    experiences = storage.load_experiences()
except Exception as exc:
    st.error(f"Unable to load experiences from `{data_dir}/experiences.json`: {exc}")
    st.stop()

experience_map = {exp.id: exp for exp in experiences}

jd = st.text_area("Job Description", height=220, placeholder="Paste the JD here...")

selected_ids = st.multiselect(
    "Select experiences",
    options=[exp.id for exp in experiences],
    format_func=lambda exp_id: f"{exp_id} - {experience_map[exp_id].title} @ {experience_map[exp_id].company}",
)

st.markdown("#### Suggestions JSON (optional)")
st.caption("Object keyed by experience id. Leave as `{}` for defaults.")
suggestions_json = st.text_area(
    "suggestions_json",
    value="{}",
    height=160,
    label_visibility="collapsed",
)

if st.button("Generate tailored bullets", type="primary"):
    if not jd.strip():
        st.error("Please provide a job description.")
        st.stop()
    if not selected_ids:
        st.error("Please select at least one experience.")
        st.stop()

    try:
        raw_suggestions = json.loads(suggestions_json or "{}")
        suggestions_by_id = {
            key: SuggestionPayload.model_validate(value) for key, value in raw_suggestions.items()
        }
    except Exception as exc:
        st.error(f"Invalid suggestions JSON: {exc}")
        st.stop()

    orchestrator = CliOrchestrator(Path(data_dir), use_mock_llm=use_mock_llm)

    try:
        session = orchestrator.generate_once(
            job_description=jd,
            selected_ids=selected_ids,
            suggestions_by_id=suggestions_by_id,
            print_output=False,
        )
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    st.success(f"Generated session: {session.session_id}")
    for exp_id in selected_ids:
        draft = session.drafts_by_experience[exp_id]
        exp = experience_map[exp_id]
        st.markdown(f"### {exp.title} @ {exp.company} (`{exp_id}`)")
        if not draft.bullets_current:
            st.info("No bullets generated.")
            continue
        for idx, bullet in enumerate(draft.bullets_current, start=1):
            st.write(f"{idx}. {bullet}")
