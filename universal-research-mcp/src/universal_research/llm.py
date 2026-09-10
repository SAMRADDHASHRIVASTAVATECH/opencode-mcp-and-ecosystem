"""Optional OpenAI-compatible reasoning client (#66, #67).

Used only when UR_RESEARCH_MODEL_BASE_URL is configured and UR_USE_LLM=true.
The whole research system works without it (deterministic fallbacks). Small
models are fine because prompts passed here are bounded and structured.
"""
from __future__ import annotations

import json
import os
from typing import Optional

from . import network
from .errors import ConfigError


class ReasoningClient:
    def __init__(self, settings):
        self.settings = settings

    @property
    def enabled(self) -> bool:
        s = self.settings
        return bool(s.use_llm and s.research_model_base_url and s.research_model_name)

    def complete(self, system: str, prompt: str,
                 max_tokens: int = 600, temperature: float = 0.2) -> str:
        if not self.enabled:
            raise ConfigError("reasoning model not enabled/configd")
        s = self.settings
        url = s.research_model_base_url.rstrip("/")
        if not url.endswith("/chat/completions"):
            url = url + "/v1/chat/completions" if "/v1" not in url \
                else url + "/chat/completions"
        headers = {"Content-Type": "application/json"}
        if s.research_model_api_key:
            headers["Authorization"] = f"Bearer {s.research_model_api_key}"
        body = {"model": s.research_model_name,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": prompt}],
                "max_tokens": max_tokens, "temperature": temperature,
                "stream": False}
        # NOTE: the reasoning endpoint is an operator-configured service (e.g. a
        # local Ollama/OpenAI-compatible server), not untrusted fetched content,
        # so it is reached directly rather than through the SSRF-guarded fetcher.
        try:
            resp = httpx.post(url, headers=headers, json=body,
                              timeout=httpx.Timeout(60.0))
        except Exception as exc:  # noqa: BLE001
            raise ConfigError(f"reasoning call failed: {exc}")
        if resp.status_code != 200:
            raise ConfigError(f"reasoning HTTP {resp.status_code}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            raise ConfigError("unexpected reasoning response shape")


def safe_json(text: str) -> Optional[dict]:
    """Best-effort parse of a model's JSON (may include ``` fences)."""
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t.startswith("json"):
            t = t[4:]
    try:
        return json.loads(t)
    except Exception:
        return None
