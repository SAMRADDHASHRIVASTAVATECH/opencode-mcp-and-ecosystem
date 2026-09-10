# Future Expansion Roadmap — Canonical Reference

> Source: PART XIX — FUTURE EXPANSION ROADMAP. The authoritative forward plan. This is roadmap *context*
> (a planning/scope reference), not an implementable runtime capability. It is preserved for completeness
> and traceability; see COVERAGE.md for its classification.

## 19.1 Phase 1 — Core Hardening (Q3–Q4 2025)
- Complete T0/T1 hardware adaptation validation on reference hardware.
- Release Plugin SDK v1.0 and developer documentation.
- Integrate local LLM support (llama.cpp) for T1 hardware.
- Ship Android companion app (CATLX Mobile v1.0).
- Complete audit-log signing and tamper detection.
- Publish Plugin Marketplace alpha with a curated initial catalog.

## 19.2 Phase 2 — Provider Expansion & Multi-Agent (Q1–Q2 2026)
- Integrate OpenAI and Anthropic Claude API providers.
- Launch multi-agent framework: multiple concurrent specialized agents with task handoff.
- Deploy vLLM-based local inference server for T2+ hardware.
- Complete the Kubernetes Helm chart for enterprise deployment.
- Enable agent collaboration: agents share workspace memory and coordinate via the Event Bus.
- Launch Developer Portal and Plugin Marketplace public beta.

## 19.3 Phase 3 — Sensory Expansion (Q3–Q4 2026)
- Computer vision: real-time object detection and scene understanding via camera.
- iOS companion app (CATLX Mobile for iOS).
- Extended Reality (XR) shell: HUD overlay for AR headsets (Meta Quest, Apple Vision Pro).
- Wearable integration: voice commands from smartwatch microphone; notifications on watch face.
- Multi-room audio: route voice commands and TTS responses to smart speakers on LAN.

## 19.4 Phase 4 — Collaborative & Enterprise (2027)
- Multi-user support: shared CATLX instance with per-user memory partitions and permission scopes.
- Enterprise SSO: SAML/OIDC integration for user authentication.
- Centralized enterprise plugin registry with policy enforcement.
- CATLX Network: peer-to-peer CATLX instances that can delegate tasks to each other.
- Compliance certifications: SOC 2 Type II, ISO 27001 for enterprise customers.
- Regulatory audit export: structured export of audit logs for GDPR, HIPAA, and SOX compliance.

## 19.5 Long-Term Vision
CATLX is designed to become what computing has always promised but never delivered: a system that
understands you, adapts to you, runs with you everywhere, and grows more capable over time without growing
more complex to use. Every architectural decision — from the Capability Router's adaptive scaling to the
Memory Broker's coherence protocol to the portable file-backed registries — serves that vision. It does not
compromise, does not have a Lite edition, does not require the cloud to be useful. One system, for every
person, on every machine, doing everything.
