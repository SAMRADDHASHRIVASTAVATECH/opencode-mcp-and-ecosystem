# Workflow: Simulate Last

```
final-ish meshes → final animation → collision proxies
→ scale check (meters!) → gravity → colliders → force fields
→ quality → bake to disk (cache/) → verify (D127)
```

Rule: fake first (decision 5.6 / 5.18). Sim only when faking is harder or visibly worse.

Cloth/hair/fluid need final animation AND final-ish meshes. Never sim on a moving target.
