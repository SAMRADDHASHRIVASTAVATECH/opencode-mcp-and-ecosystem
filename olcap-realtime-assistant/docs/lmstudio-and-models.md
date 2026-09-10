# LM Studio & model configuration

## LM Studio (spec 22)

1. Install LM Studio and start its local server (default `http://127.0.0.1:1234/v1`).
2. Load a model (e.g. a small coder/instruct model for realtime; a larger one for deeper
   reasoning).
3. Point the assistant at it:

```bash
OLCAP_REASONING_PROVIDER=lmstudio
LM_STUDIO_ENDPOINT=http://127.0.0.1:1234/v1
OLCAP_REASONING_MODEL=qwen2.5-coder-7b-instruct
```

The `LmStudioProvider` supports streaming, cancellation, timeout, model listing, and
context-window awareness. The assistant manages rolling context so realtime operation
does not repeatedly overflow the model's window.

## Model abstraction & switching

`ModelRouter` is provider-agnostic. Switch models without rewriting code:

* `model.list` — list models per provider.
* `model.get_status` — active provider + availability.
* `model.set_provider(provider)` — switch active provider (`lmstudio`/`openclaw`).
* Config `reasoning.low_latency_model` / `strong_model` allow mode-aware model choice.

## Fallback (spec 32)

`reasoning.fallbacks` lists providers tried after the primary, e.g.:

```jsonc
{ "reasoning": { "provider": "lmstudio", "fallbacks": ["openclaw"] } }
```

Important: cloud models are only ever used when `privacy.cloud_processing=true`. The
assistant never silently sends private data to a cloud provider while cloud processing is
disabled, and it exposes the active provider through `model.get_status` / `assistant.health`.

## Health

`assistant.health().reasoning` and `model.get_status` show per-provider availability so
you can confirm whether a model is actually reachable before relying on it.
