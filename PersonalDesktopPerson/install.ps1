$ErrorActionPreference='Stop'
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Python 3.11+ is required.' }
py -3 -c "import sys; assert sys.version_info >= (3,11), sys.version"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
New-Item -ItemType Directory -Force runtime | Out-Null
.\.venv\Scripts\python.exe -m personal_desktop_person.health
.\.venv\Scripts\python.exe configure_opencode.py
Write-Host 'Installed. Edit opencode.jsonc paths, then import it into OpenCode.'
