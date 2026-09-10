#!/usr/bin/env bash
# Run the full test suite (individual skills + whole-system orchestration +
# large-doc / state tests).
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pytest tests/ -v "$@"
