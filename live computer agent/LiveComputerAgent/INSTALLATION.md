# Installation
1. Use 64-bit Windows 10/11 and Python 3.11–3.12 from python.org.
2. Open PowerShell in the package directory and run `Set-ExecutionPolicy -Scope Process Bypass`, then `.\install.ps1`.
3. Optionally install Tesseract OCR from its trusted project/distributor; ensure `tesseract.exe` is on PATH. The installer does not fetch it.
4. Review `config/default.json`; keep process launch disabled unless needed.
5. Copy the MCP entry from `opencode.json.example` into OpenCode's configuration, replacing the absolute path.
6. Restart OpenCode and call `health_check`, then `start_live_session`.
7. Run `.\.venv\Scripts\pytest.exe -m "not windows_live"`; then run Windows acceptance tests intentionally with `LCA_RUN_WINDOWS_LIVE=1`.

For local autonomous planning set environment variables `LCA_LLM_URL=http://127.0.0.1:PORT/v1`, `LCA_LLM_MODEL=...`. Remote providers may receive structured screen text; review privacy first.
