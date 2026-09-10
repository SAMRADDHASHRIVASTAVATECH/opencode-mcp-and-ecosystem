$ErrorActionPreference="Stop"
if ($PSVersionTable.Platform -and $PSVersionTable.Platform -ne "Win32NT") { throw "Windows is required for live control." }
$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $py) { throw "Python 3.11 or 3.12 is required. Install it from python.org, then rerun." }
$ver=& py -3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$ver -lt [version]"3.11") { throw "Python >=3.11 required; found $ver" }
& py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[windows,test]"
New-Item -ItemType Directory -Force runtime,tools,cache,models,temporary | Out-Null
& .\.venv\Scripts\python.exe -m live_computer_agent.health
Write-Host "Installed. Tesseract OCR is optional and must be installed separately from its trusted installer if OCR is needed."
Write-Host "Run: .\launch-mcp.ps1"
