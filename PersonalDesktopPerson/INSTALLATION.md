# Installation
## Windows
Install Python 3.11+ and optionally Node.js 20+ for the separate computer-use MCP. Run `powershell -ExecutionPolicy Bypass -File install.ps1`. Review `config/default.json`. Optionally install the audited computer-use server with `npm install -g @qwen-code/open-computer-use`. Merge `opencode.jsonc` into OpenCode and use absolute paths.

## macOS/Linux
Run `bash install.sh`; grant only the accessibility/screen permissions required by the chosen computer-use server. Wayland and macOS intentionally require user permission.

## Provider
Set `provider_url` to an OpenAI-compatible base ending before `/chat/completions`, set `provider_model`, and place the key in environment variable `PDP_API_KEY`. Local providers usually need no key. Screen content should not be sent to remote providers without explicit consent.
