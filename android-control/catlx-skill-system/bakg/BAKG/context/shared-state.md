# Shared Production State

When BAKG operates in whole-system mode (and when skills chain), they share a production state object. Skills read from it and write to it. Individual-skill mode may start with a partial state.

## State schema

```yaml
project:
  type: short-film | loop | cutscene | turntable | vfx-shot | environment-film | experimental | other
  style: realistic | stylized | anime | cartoon | hybrid | painterly | other
  medium: short-film | loop | game-cutscene | still | realtime | other
  logline: string
  emotional_goals: [string]
  fps: 24 | 25 | 30 | 60
  resolution: [w, h]
  aspect: string
  engine: cycles | eevee | workbench | hybrid
  units: metric-meters
  naming_legend: string

story:
  beats: []
  shot_list: []
  duration_seconds: number

world:
  bible: string
  climate: string
  time_of_day: string
  tech_magic_rules: string
  palette: []
  weather: string

characters: []   # each: name, concept, design, sheet_status, locomotion_class, mass, surface
creatures: []
assets: []       # type, name, status, file
shots: []        # id, status, owner, camera, duration, dependencies

locks:
  style: false
  animatic: false
  blockout: false
  model: false
  lookdev: false
  rig: false
  animation: false
  sim: false
  lighting: false
  render: false
  edit: false

budgets:
  poly_hero: number
  poly_bg: number
  texture_hero: string   # 2k/4k/8k
  render_time_per_frame: string
  memory: string

gates_passed: []
open_issues: []
style_rules: []          # D138
addons_manifest: []
```

## Shot status ladder

`planned → blocked → splined → animated → sim'd → lit → rendered → comped → approved`

Each status change is a review point (D127).

## How skills use state

- **Read** before acting (do not contradict a lock).
- **Write** outputs into the matching fields.
- **Never** silently reverse a lock; flag a feedback loop instead.
- If a required field is missing and the skill is running independently, ask or assume the cheapest valid default and record the assumption.
