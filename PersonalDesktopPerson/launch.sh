#!/usr/bin/env sh
cd "$(dirname "$0")"; export PDP_CONFIG="$PWD/config/default.json"; exec .venv/bin/python -m personal_desktop_person
