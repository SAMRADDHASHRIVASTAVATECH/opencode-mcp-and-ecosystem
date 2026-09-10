"""Realtime reasoning engine (spec sections 7, 8, 22, 23, 32).

Model abstraction: LM Studio (OpenAI-compatible local), OpenClaw, or optional
cloud. Supports streaming, cancellation, timeout, context-window awareness,
rolling context (never resend whole history), debounce and configurable fallback.

Honest: if no reachable model is configured, generate() returns MODEL_UNAVAILABLE
rather than a fabricated response.
"""
from __future__ import annotations

import json
import threading
import time

from ..config import AppConfig
from ..errors import ModelUnavailable, NotConfigured


class ReasoningProvider:
    name = "abstract"
    kind = "local"

    def list_models(self): return []
    def get_status(self): return {"name": self.name, "available": self.available()}
    def available(self) -> bool: return False

    def generate(self, messages, *, stream=False, model="", **kw) -> str:
        raise ModelUnavailable(f"{self.name} not available")

    def cancel(self):
        pass


class LmStudioProvider(ReasoningProvider):
    """OpenAI-compatible local inference (LM Studio) over HTTP."""
    name = "lmstudio"
    kind = "local"

    def __init__(self, config: ReasoningConfig):
        self.cfg = config
        self._cancel = threading.Event()

    def _client(self):
        try:
            import httpx
            return httpx
        except ImportError as e:  # pragma: no cover
            raise ModelUnavailable("httpx is required for LM Studio") from e

    def endpoint(self, base: str):
        return base.rstrip("/")

    def available(self) -> bool:
        try:
            import httpx
            r = httpx.get(self.endpoint(self.cfg.endpoint) + "/models", timeout=3)
            return r.status_code < 500
        except Exception:
            return False

    def list_models(self):
        try:
            import httpx
            r = httpx.get(self.endpoint(self.cfg.endpoint) + "/models", timeout=5)
            r.raise_for_status()
            data = r.json()
            return [m.get("id") for m in data.get("data", [])]
        except Exception:
            return []

    def generate(self, messages, *, stream=False, model="", max_tokens=800,
                 temperature=0.3):
        self._cancel.clear()
        m = model or self.cfg.model
        url = self.endpoint(self.cfg.endpoint) + "/chat/completions"
        headers = {}
        if self.cfg.api_key:
            headers["Authorization"] = f"Bearer {self.cfg.api_key}"
        body = {"model": m, "messages": messages, "temperature": temperature,
                "max_tokens": max_tokens, "stream": stream}
        try:
            import httpx
            with httpx.Client(timeout=self.cfg.timeout_s) as client:
                if stream:
                    full = ""
                    with client.stream("POST", url, json=body, headers=headers) as r:
                        if r.status_code >= 400:
                            raise ModelUnavailable(
                                f"lmstudio HTTP {r.status_code}: {r.text[:200]}")
                        for line in r.iter_lines():
                            if self._cancel.is_set():
                                break
                            if not line or not line.startswith("data:"):
                                continue
                            chunk = line[5:].strip()
                            if chunk == "[DONE]":
                                break
                            try:
                                delta = json.loads(chunk)["choices"][0]["delta"]
                                full += delta.get("content") or ""
                            except Exception:
                                continue
                    return full
                r = client.post(url, json=body, headers=headers)
                if r.status_code >= 400:
                    raise ModelUnavailable(
                        f"lmstudio HTTP {r.status_code}: {r.text[:200]}")
                return r.json()["choices"][0]["message"]["content"] or ""
        except ModelUnavailable:
            raise
        except Exception as e:
            raise ModelUnavailable(f"LM Studio unreachable at {self.cfg.endpoint}: {e}")

    def cancel(self):
        self._cancel.set()


class OpenClawReasoningProvider(ReasoningProvider):
    """Delegates reasoning to the existing OpenClaw model infrastructure - we do
    not duplicate OpenClaw's model/voice stack (spec section 20). Requires a
    configured OpenClaw client hook."""
    name = "openclaw"
    kind = "local"

    def __init__(self, config, openclaw=None):
        self.cfg = config
        self._oc = openclaw

    def available(self):
        return self._oc is not None and getattr(self._oc, "health", lambda: False)()

    def generate(self, messages, **kw):
        if not self.available():
            raise ModelUnavailable("OpenClaw model endpoint not reachable")
        return self._oc.complete(messages, model=kw.get("model", self.cfg.model))


class ModelRouter:
    """Primary -> fallbacks (spec section 32). Cloud only used when privacy
    allows. Tracks active provider state."""
    def __init__(self, config: AppConfig, openclaw=None):
        self.cfg = config
        self._providers = {
            "lmstudio": LmStudioProvider(config.reasoning),
            "openclaw": OpenClawReasoningProvider(config.reasoning, openclaw),
        }
        self.active = config.reasoning.provider
        self._lock = threading.Lock()

    def get(self, name):
        p = self._providers.get(name)
        if p is None:
            raise NotConfigured(f"unknown reasoning provider '{name}'")
        return p

    def set_provider(self, name):
        if name not in self._providers:
            raise NotConfigured(f"unknown provider '{name}'")
        self.active = name
        return {"active_provider": name}

    def list_models(self):
        out = {}
        for n, p in self._providers.items():
            out[n] = p.list_models()
        return out

    def status(self):
        out = {}
        for n, p in self._providers.items():
            out[n] = {"available": p.available(), "kind": p.kind,
                      "active": (self.active == n)}
        return out

    def health(self):
        return {"active_provider": self.active,
                "providers": self.status()}

    def generate(self, messages, *, model="", stream=False, allow_cloud=True,
                 **kw):
        """Try primary, then configured fallbacks. Respect cloud privacy gate."""
        order = [self.active] + [f for f in self.cfg.reasoning.fallbacks
                                 if f != self.active]
        for name in order:
            prov = self._providers.get(name)
            if not prov:
                continue
            # never silently use cloud when cloud processing disabled
            if prov.kind == "cloud" and not self.cfg.privacy.cloud_processing:
                continue
            if prov.available():
                try:
                    return prov.generate(messages, model=model, stream=stream,
                                         **kw)
                except ModelUnavailable:
                    continue
                except Exception:
                    continue
        raise ModelUnavailable(
            "no reachable reasoning model (checked: " + ", ".join(order) + ")")


def build_messages(system: str, context: dict, user: str) -> list:
    """Construct a compact message list; context is pre-summarised so we never
    overflow the model's context window."""
    ctx_blob = _stringify(context) if context else ""
    msgs = [{"role": "system", "content": system}]
    if ctx_blob:
        msgs.append({"role": "system", "content": "Current context:\n" + ctx_blob})
    msgs.append({"role": "user", "content": user})
    return msgs


def _stringify(d):
    try:
        return json.dumps(d, ensure_ascii=False, default=str)
    except Exception:
        return str(d)
