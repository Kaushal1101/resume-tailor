from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.domain.entities import SuggestionPayload
from src.modules.cli_orchestrator import CliOrchestrator
from src.modules.storage import JsonStorage


st.set_page_config(page_title="Resume Tailor Prototype", layout="wide")
st.title("Resume Tailor Prototype")
st.caption("Simple UI for testing JD -> tailored bullets generation with stubbed inputs.")

STUB_EXPERIENCE_IDS = ["exp_backend_1", "exp_data_1"]
STUB_SUGGESTIONS = {
    "exp_backend_1": SuggestionPayload(
        keywords=["python", "fastapi", "api design"],
        tools=["FastAPI", "PostgreSQL"],
        skills=["backend engineering", "system design"],
        bullet_count=3,
    ),
    "exp_data_1": SuggestionPayload(
        keywords=["etl", "analytics", "data quality"],
        tools=["Airflow", "SQL"],
        skills=["data engineering", "pipeline reliability"],
        bullet_count=2,
    ),
}

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

st.markdown("#### Stubbed Inputs")
st.caption("Experiences and suggestions are fixed for now; only JD is editable.")

selected_ids = [exp_id for exp_id in STUB_EXPERIENCE_IDS if exp_id in experience_map]
if not selected_ids:
    st.error(
        "None of the stub experience IDs were found in `data/experiences.json`. "
        "Expected IDs: exp_backend_1, exp_data_1."
    )
    st.stop()

for exp_id in selected_ids:
    exp = experience_map[exp_id]
    st.write(f"- {exp_id}: {exp.title} @ {exp.company}")

if st.button("Generate tailored bullets", type="primary"):
    if not jd.strip():
        st.error("Please provide a job description.")
        st.stop()
    orchestrator = CliOrchestrator(Path(data_dir), use_mock_llm=use_mock_llm)

    try:
        session = orchestrator.generate_once(
            job_description=jd,
            selected_ids=selected_ids,
            suggestions_by_id={exp_id: STUB_SUGGESTIONS[exp_id] for exp_id in selected_ids},
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
