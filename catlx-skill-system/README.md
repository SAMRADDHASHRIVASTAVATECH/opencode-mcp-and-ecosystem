# CATLX Universal AI OS — Skill System

A complete, autonomous, interconnected **skill ecosystem** compiled from the single source document
`CATLX_Universal_AI_OS_Specification.pdf` (Master Architecture Specification, v1.0.0, Rev A).

**Scope:** Windows 10 / 11 only, and **USB-free** (USB drive tiering is removed).

**Design:** ONE source of truth → canonical `knowledge/` layer → **many independently callable, normal
skills** (OpenCode-compatible `SKILL.md`) connected by a dependency graph, a routing index, an automatic
delegation protocol, and progressive context loading.

---

## What you get

| Artifact | File | Purpose |
|---|---|---|
| Universal Orchestrator | `skills/catlx-orchestrator/SKILL.md` | **Universal Mode.** Auto-routes natural-language requests; a lightweight, graph-aware front door (not a second knowledge base) |
| Root gateway skill | `skills/catlx/SKILL.md` | **Direct Mode** entry; routes to the right subsystem; drives delegation + progressive loading |
| 18 subsystem skills | `skills/catlx-*/SKILL.md` | Each an independently callable capability |
| Canonical knowledge (single source of truth) | `knowledge/**` | Glossary, rules (R1–R16), component-lifecycle & Windows rules, references per source part |
| Skills index | `INDEX.md` | Discover skills, capabilities, dependencies, delegation, sources |
| Manifest | `MANIFEST.md` + `metadata/skills-registry.json` | Machine-readable registry (same data as `INDEX.md`) |
| Dependency graph | `DEPENDENCY-GRAPH.md` + `metadata/dependency-graph.json` | Real `depends_on` (acyclic) + `delegates_to` (guarded) edges |
| Capability index + intent map | `metadata/capability-index.json` | Deterministic routing core for the orchestrator & small local models |
| Source map | `SOURCE-MAP.md` | Traceability: source section → canonical knowledge → artifact |
| Coverage matrix | `COVERAGE.md` | Verifies full source coverage; no orphaned knowledge/skills |
| Workflows / templates / examples | `workflows/`, `templates/`, `examples/` | Source structures preserved (DSL, manifests, policies, JSON/YAML) |
| Validator + generators | `scripts/` | Validate SKILL.md, regenerate registry, graph & routing index |

---

## Two entry modes (same graph, same rules)

- **Direct Mode (`catlx` or any `catlx-*`):** the user names a skill; it runs and delegates internally.
- **Universal Mode (`catlx-orchestrator`):** the user activates it once, then asks in plain English. It
  routes via `metadata/capability-index.json` (intent→skill map) + the registry, then the selected skill
  auto-delegates recursively. Both modes resolve through the same canonical knowledge, registry, graph,
  references, and workflows. The orchestrator itself is **not** a second knowledge base.

## Automatic skill-to-skill invocation

Every skill owns its part and, if it needs a capability it does **not** own, it:
- identifies the missing capability,
- finds the best match in `INDEX.md` / `metadata/skills-registry.json`,
- checks the active-skill chain (cycle protection),
- invokes the target skill with **minimal context**,
- incorporates the result and continues.

Delegation may recurse (`A → B → C → D`) and then unwind (`D → C → B → A → user`). The user normally invokes
**only the appropriate start skill** (or lets the root/orchestrator route).

## Progressive loading

Only the requested subsystem skill(s) and the canonical references the task needs are loaded. The root skill
does **not** hold the whole knowledge base. Follow the minimal, sufficient dependency chain — never load the
entire skill corpus.

---

## Re-generating the registry, graph & routing

After editing any `SKILL.md` (frontmatter or metadata), regenerate to keep the index, graph, and routing in
sync:

```powershell
cd catlx-skill-system
python scripts/build_registry.py   # validates SKILL.md + writes metadata/skills-registry.json
python scripts/gen_graph.py        # writes metadata/dependency-graph.json
python scripts/build_routing.py    # writes metadata/capability-index.json (intent→skill map)
```

`build_registry.py` validates name rules, folder-name match, description length, and valid frontmatter, and
exits non-zero if any skill is invalid.

---

## Component lifecycle policy (reuse → install → adapt → create)

The ecosystem never creates a new component as a default. For any missing capability, skill, dependency,
workflow, reference, helper, adapter, or template, it uses this order:

1. **Reuse** an existing local component (resolve aliases / equivalent capabilities first).
2. **Use** an already-registered component from the registry.
3. **Install** a suitable existing, trusted, supported component → validate → register → connect → use.
4. **Adapt** an existing compatible component via a small persistent adapter/wrapper.
5. **Create only as last resort** — then place it in the permanent ecosystem immediately (stable id, canonical
   location, register, capability index + dependency graph, provenance, reuse).

Rules: avoid `/tmp`/scratch for anything reusable; promote reusable artifacts permanently; never recreate
already-generated components (`Skill X 2`/`new`/`temp`) — extend the existing one; never create a second
competing knowledge source; connect everything back to the canonical `knowledge/` layer and shared graph.

Canonical policy: `knowledge/rules/component-lifecycle.md`. The Universal Orchestrator and every individual
skill enforce this.

## Provenance policy

- **Exact:** tables, lists, JSON/YAML, and step sequences preserved faithfully.
- **Adapted:** Windows-only / USB-free conversion, documented in `knowledge/rules/windows-rules.md` and the
  relevant skill.
- **Inferred:** skill boundaries, dependencies, delegation, and the index/graph/manifest structure are
  structural metadata — **not** domain knowledge invented from the source. Anything inferred is labeled as
  such.

## Not included

- OpenCode installation/import instructions (removed from this deliverable).
- USB drive tiering (removed per scope).
- Linux/macOS mechanisms (replaced with Windows equivalents).
- The **roadmap** (Part XIX) is preserved as reference/context, not an executable capability.
