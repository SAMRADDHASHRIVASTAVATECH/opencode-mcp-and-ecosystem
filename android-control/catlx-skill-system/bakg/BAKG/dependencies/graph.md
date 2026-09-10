# BAKG Dependency Graph (human-readable)

```
                    ┌─────────────────────┐
                    │  bakg-orchestrator  │
                    │  decision-engine    │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ↓                  ↓                  ↓
     preproduction      character-design     blender-foundations
            ↕                  ↓                  ↓
     grease-pencil      sculpting-anatomy → modeling
                               ↓                  ↓
                          lookdev ←───────────────┘
                               ↓
                        costume-groom
                               ↓
                            rigging ⇄ animation
                               ↓
                          environment
                               ↓
                     simulation → vfx
                               ↓
                  cinematography → lighting
                               ↓
                          render-comp
                               ↓
                     production-finishing
```

Shared context (`context/`) and shared knowledge (`knowledge/`) sit under every node.

Machine-readable edges: `dependencies/skill-graph.yaml`.
Domain-level edges: `knowledge/system/03-relationship-map.md`.
