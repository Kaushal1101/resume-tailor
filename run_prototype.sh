#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source ".venv/bin/activate"
python -m pip install -r requirements.txt

JD=""
EXPERIENCE_IDS=""
SUGGESTIONS_JSON="{}"
USE_MOCK_LLM=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --jd)
      JD="${2:-}"
      shift 2
      ;;
    --experience-ids)
      EXPERIENCE_IDS="${2:-}"
      shift 2
      ;;
    --suggestions-json)
      SUGGESTIONS_JSON="${2:-}"
      shift 2
      ;;
    --use-mock-llm)
      USE_MOCK_LLM=true
      shift 1
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: ./run_prototype.sh [--jd \"...\"] [--experience-ids \"...\"] [--suggestions-json '{...}'] [--use-mock-llm]"
      exit 1
      ;;
  esac
done

if [ -z "$JD" ]; then
  read -r -p "Paste Job Description: " JD
fi

if [ -z "$EXPERIENCE_IDS" ]; then
  echo "Available experience ids are in data/experiences.json (for example: exp_backend_1,exp_data_1)."
  read -r -p "Enter comma-separated experience ids: " EXPERIENCE_IDS
fi

if [ "$SUGGESTIONS_JSON" = "{}" ]; then
  echo "Optional suggestions JSON (press Enter for defaults)."
  read -r -p "Suggestions JSON: " INPUT_SUGGESTIONS
  if [ -n "${INPUT_SUGGESTIONS:-}" ]; then
    SUGGESTIONS_JSON="$INPUT_SUGGESTIONS"
  fi
fi

CMD=(
  python -m src.cli.main generate
  --jd "$JD"
  --experience-ids "$EXPERIENCE_IDS"
  --suggestions-json "$SUGGESTIONS_JSON"
)

if [ "$USE_MOCK_LLM" = true ]; then
  CMD+=(--use-mock-llm)
fi

"${CMD[@]}"
