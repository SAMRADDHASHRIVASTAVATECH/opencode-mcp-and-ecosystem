# AI Provider Architecture — Canonical Reference

> Source: PART VIII — AI PROVIDER ARCHITECTURE (Windows-only adaptation). The single authoritative source
> for the Provider Abstraction Layer, current/future providers, routing & failover, cost routing, and
> local LLM integration.

## 8.1 Provider Abstraction Layer (PAL)
CATLX never calls an AI provider directly from application code. All inference passes through the PAL — a
unified interface normalizing request/response formats across providers. It exposes a single
`ProviderClient` with methods: `complete()`, `streamComplete()`, `embed()`, `transcribe()`,
`synthesize()`. Callers are unaware of which provider serves a request.

## 8.2 Current Providers

| Provider | Capabilities used | Notes |
|---|---|---|
| Google AI Studio | Text completion (Gemini Pro/Flash), embedding, multimodal | Primary for complex reasoning; supports 1M-token context |
| Groq | Fast text completion (Llama 3, Mixtral, Gemma), Whisper STT | Primary for speed-critical tasks; sub-100 ms first-token latency |
| Hugging Face | Specialized models via Inference API, custom fine-tuned models | Domain-specific tasks; 40,000+ public models |

## 8.3 Future Providers

| Provider / Engine | Status |
|---|---|
| OpenAI (GPT-4o / o-series) | Planned — Phase 2 |
| Anthropic Claude API | Planned — Phase 2 |
| llama.cpp (local inference) | Planned — Phase 1 local model support |
| vLLM (GPU-optimized serving) | Planned — T2/T3 hardware only |
| Ollama (local model manager) | Planned — T1+ hardware |
| Custom fine-tuned models | Planned — user-provided GGUF or safetensors |
| Azure OpenAI | Planned — enterprise customers |
| AWS Bedrock | Planned — enterprise customers |

## 8.4 Provider Routing & Failover

The Provider Router selects the best provider per request based on: request type (completion vs embedding
vs STT vs TTS), latency requirements, token budget, current provider health, and hardware tier (local
providers preferred on T2+). Routing rules are declared in a **declarative routing policy file (YAML)** the
user can override.

### 8.4.1 Failover Protocol
1. Primary provider called with timeout = configurable (default 10 s for completion, 3 s for fast-path).
2. If timeout exceeded or error returned: mark provider **degraded** (30 s cooldown); select next provider
   in the routing priority list.
3. If all remote providers degraded: route to the best available local model (if T1+).
4. If no local model available (T0): queue the request with user notification; retry when the provider
   recovers.
5. All failover events logged to telemetry with correlation IDs for post-hoc analysis.

### 8.4.2 Cost Optimization Router
For non-latency-critical tasks (background summarization, memory extraction, batch embedding), the Cost
Router selects the cheapest provider tier meeting quality. **Fast models** (Groq Llama 3 8B) preferred for
classification/extraction. **Large models** (Gemini Pro) reserved for complex reasoning, code generation,
and multi-step planning.

## 8.5 Local LLM Integration

On T1+ hardware CATLX can host local LLM models. The **Local Model Manager** handles: model download and
verification (GGUF from HuggingFace), quantization-level selection (Q4_K_M for T1, Q8_0 for T2), inference
server startup (llama.cpp server, or vLLM on T2+), and health monitoring. The local server exposes an
**OpenAI-compatible API on localhost**, making it a drop-in replacement for any remote provider in the
routing table.

### Recommended local models by tier

| Hardware tier | Recommended models |
|---|---|
| T1 (16 GB RAM, no GPU) | Llama 3.2 3B Q8_0, Phi-3 mini Q8_0, Gemma 2 2B Q8_0 |
| T2 (64 GB RAM, RTX GPU) | Llama 3.1 70B Q4_K_M, Qwen 2.5 72B Q4, Mistral Large Q4 |
| T3 (enterprise server) | Full precision Llama 3.1 405B, custom fine-tuned models |

## Cross-references
- Consumed by: `skills/catlx-ai-provider/SKILL.md`.
- Delegates to: `catlx-memory` (RAG context), `catlx-telemetry` (correlation IDs), `catlx-security`.
- Routing policy template: `templates/providers.yaml`.
- Source tree: `knowledge/references/folder-structure.md` (`ai-providers/`); `config/providers.yaml`.
