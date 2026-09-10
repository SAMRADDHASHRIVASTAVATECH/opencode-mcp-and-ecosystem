# Delegation Rules (system-wide)

Skills may delegate. They must not vanish into each other.

## Legal delegation

A skill may call another skill when:
- The other skill owns the domain (D#) in question.
- The calling skill needs a **decision**, a **prerequisite check**, or a **specialized procedure**.
- The call is bounded (one question, one output contract).

## Illegal delegation

- Calling every related skill "just in case".
- Re-implementing another skill's procedure instead of delegating.
- Delegating backward through a lock (e.g., animation asking modeling to rebuild the character) without raising a feedback loop.
- Delegating to a skill whose prerequisites are not met, without first routing through those prerequisites.

## Typical delegations

| From | To | When |
|---|---|---|
| any | decision-engine | A documented fork appears |
| any | bakg-orchestrator | Request spans multiple capabilities |
| character-design | preproduction | World rules constrain the design |
| modeling | sculpting-anatomy | Anatomy/proportion numbers needed |
| modeling | character-design | Silhouette/sheet missing |
| sculpting-anatomy | modeling | Retopo / topology after sculpt |
| lookdev | decision-engine | Style/shading/engine choice |
| costume-groom | simulation | Cloth/hair dynamics |
| rigging | modeling | Deformation fails because of topology |
| animation | rigging | Controls unusable or missing |
| animation | costume-groom | Secondary cloth/hair |
| environment | lighting | World light / weather light |
| simulation | vfx | Effect design (layered method) |
| vfx | render-comp | Integration, glows, holds |
| cinematography | lighting | Exposure/mood for the shot |
| lighting | render-comp | Engine limits, volume cost |
| render-comp | lighting / lookdev | Noise, fireflies, wrong look |
| production-finishing | any | QC failure at a gate |
| grease-pencil | preproduction | Boards / animatic |
| grease-pencil | render-comp | Hybrid 2D-3D comp |

## Output handoff

The callee returns its **Outputs** block (see each SKILL.md). The caller merges them into shared state and continues.
