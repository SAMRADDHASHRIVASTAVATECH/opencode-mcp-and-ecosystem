---
name: catlx-ai-provider
description: "Handles the CATLX AI provider architecture: the Provider Abstraction Layer (PAL), current and future providers, provider routing and failover protocol, the cost optimization router, and local LLM integration (llama.cpp/vLLM with OpenAI-compatible API). Use when the user asks about which AI provider CATLX uses, provider failover, routing policies, the cost router, local models, embeddings, or how AI inference is abstracted."
metadata:
  catlx: subsystem
  category: architecture
  subsystem: AI_Provider_Layer
  capability: ai-provider-routing
  version: "1.0.0"
  source: "PART VIII §8.1-8.5"
  aliases: "ai provider, llm, model, inference, embeddings, provider routing, failover, local model, pal"
  depends-on: "catlx-capability-routing"
---

# CATLX — AI Provider Architecture

This skill owns the **AI provider abstraction and routing**: a uniform `ProviderClient` interface, a router
that picks the best provider per request, a failover protocol, cost-based routing, and local LLM hosting.

> Canonical detail: `../../knowledge/references/ai-provider.md`. Policy template:
> `../../templates/providers.yaml`. Load on demand.

---

## Purpose

Make every AI inference go through a single abstraction (`complete()` / `streamComplete()` / `embed()` /
`transcribe()` / `synthesize()`), so callers never know which provider serves a request, and so requests are
routed to the best provider for the situation (latency, cost, quality, health, hardware tier).

## When to activate

- User asks which provider is used, or how CATLX fails over between providers.
- Configuring a routing policy, local model, or quant level.
- Debugging provider latency/timeout/cost.

## What this skill handles

1. **Provider Abstraction Layer (PAL)** — normalizes requests/responses across all providers; single
   `ProviderClient` interface; callers unaware of the provider.
2. **Current providers** — Google AI Studio (Gemini Pro/Flash, embedding, multimodal, 1M-token context),
   Groq (fast completion, Whisper STT, sub-100 ms first-token), Hugging Face (specialized models,
   fine-tuned, 40k+ models).
3. **Future providers** — OpenAI, Anthropic Claude, llama.cpp, vLLM (T2/T3), Ollama (T1+), custom GGUF/
   safetensors, Azure OpenAI, AWS Bedrock (planned phases).
4. **Provider routing & failover** — choose best provider by request type, latency, token budget, health,
   and tier. Declarative routing policy in YAML (`providers.yaml`).
5. **Failover protocol** — timeout default 10 s (3 s fast-path); mark degraded (30 s cooldown); next in
   priority; all remote degraded → best local model (T1+); no local (T0) → queue + notify + retry; log with
   correlation IDs.
6. **Cost optimization router** — for non-latency-critical tasks, pick the cheapest tier meeting quality;
   fast models for classification/extraction; large models for complex reasoning/code/multi-step planning.
7. **Local LLM integration** — Local Model Manager: download/verify GGUF from HF, quantization (Q4_K_M for
   T1, Q8_0 for T2), start llama.cpp server (or vLLM T2+), health monitor; **OpenAI-compatible API on
   localhost** = drop-in replacement for any remote provider.

## Local model recommendations (by tier)

| Tier | Models |
|---|---|
| T1 (16 GB, no GPU) | Llama 3.2 3B Q8_0, Phi-3 mini Q8_0, Gemma 2 2B Q8_0 |
| T2 (64 GB, RTX) | Llama 3.1 70B Q4_K_M, Qwen 2.5 72B Q4, Mistral Large Q4 |
| T3 (enterprise) | Full precision Llama 3.1 405B, custom fine-tuned |

## Requirements / constraints

- **R6 (single access point):** no application code calls a provider directly; always through PAL.
- **R10 (local-first):** on T2+ prefer local providers; offline mode disables remote providers.
- **R13 (telemetry):** failover events logged with correlation IDs.

## Canonical knowledge it reads

`../../knowledge/references/ai-provider.md` · `../../knowledge/references/memory-architecture.md` ·
`../../knowledge/references/hardware-adaptation.md` · `../../knowledge/rules/architectural-rules.md`.

## Delegation

- **RAG context before a completion** → delegate to `catlx-memory`
  (`skill({ name: "catlx-memory" })`).
- **Which tier / whether local is available** → delegate to `catlx-hardware-adaptation`
  (`skill({ name: "catlx-hardware-adaptation" })`).
- **Where the local model server runs (container)** → delegate to `catlx-docker`
  (`skill({ name: "catlx-docker" })`).
- **Offline/capability fallback** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).
- **Credential access for provider API keys** → delegate to `catlx-security`
  (`skill({ name: "catlx-security" })`).

## Edge cases & warnings

- **Timeout/degraded provider** — follow the failover chain; do not fail the request if a fallback exists.
- **All remote degraded on T0** — queue with user notification and retry on recovery; be honest about the
  limitation.
- **Local server unavailable** — route back to remote; never silently return a fabricated completion.
- **Cost vs quality** — for latency-critical tasks use fast path; for batch/background use cost router.
- **Credential health** — never log API keys; PAL keeps them in the vault.

## Component lifecycle policy (reuse → install → adapt → create)

**NEVER create a new component as the default.** Before building/creating anything (a sub-skill, dependency,
reference, workflow, helper, adapter, or template), check, in order:
1. **Reuse** an existing local component (resolve aliases/equivalent capabilities first) — reuse, don't rebuild.
2. **Use** an already-registered component from the registry.
3. **Install** a suitable existing, trusted, supported component → validate → register → connect to the graph → use.
4. **Adapt** an existing compatible component via a small persistent adapter/wrapper instead of re-creating it.
5. **Create only as last resort** — then make it permanent immediately: stable id, canonical location, register,
   add to the capability index + dependency graph, add provenance, use, and allow future reuse.
6. Never reorganise/recreate already-generated components (no `Skill X 2` / `new` / `temp` variants); extend the
   existing one. Never create a second competing knowledge source; connect back to the canonical `knowledge/` layer.
   Promote any reusable artifact out of `/tmp`/scratch into the permanent ecosystem.

> Full policy: `../../knowledge/rules/component-lifecycle.md`.

## Source / provenance

- **Source:** PART VIII §8.1–8.5 (PAL, current/future providers, routing failover, cost router, local LLM).
- **Inferred:** none beyond Windows mapping of local server/OpenAI-compatible host.
