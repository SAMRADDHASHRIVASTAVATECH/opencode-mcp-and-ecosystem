#!/usr/bin/env sh
set -eu
python3 -c 'import sys; assert sys.version_info >= (3,11), sys.version'
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
mkdir -p runtime
.venv/bin/python -m personal_desktop_person.health
.venv/bin/python configure_opencode.py
printf '%s\n' 'Installed. Edit opencode.jsonc paths, then import it into OpenCode.'
