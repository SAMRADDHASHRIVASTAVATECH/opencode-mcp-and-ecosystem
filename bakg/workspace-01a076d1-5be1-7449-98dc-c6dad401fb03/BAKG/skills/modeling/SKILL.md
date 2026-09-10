---
name: modeling
description: Organic, hard-surface, character, and creature modeling; retopology; deformation topology — converting design into geometry that can rig, UV, and deform.
system: BAKG
version: 2.0.0
status: production
group: geometry
domains: [D17, D18, D19, D20, D23, D24, D135]
knowledge:
  - knowledge/domains/ch03-modeling.md
  - knowledge/depth/ch31-topology-depth.md
  - knowledge/system/02d-depth-supplements.md
---

# modeling

## Purpose

Convert approved design into geometry that looks right from every angle AND deforms believably through a full animation range. Topology is the most underestimated determinant of animation quality.

## Scope

D17 Organic [SIT], D18 Hard-surface [SIT], D19 Character [REQ], D20 Creature [SIT], D23 Retopology [SIT], D24 Topology [REQ], D135 Base meshes [OPT]. Sculpting craft and anatomy numbers live in `sculpting-anatomy` but this skill consumes them.

## Activation Conditions

- User asks to model, box-model, boolean, retopo, fix topology, edge flow, poles, LODs, base meshes
- Orchestrator fires modeling/retopo stages
- Feedback loop from rigging: deformation failed
- `Use modeling`

## Non-Activation Conditions

- Sculpt brush settings / dyntopo vs multires (→ sculpting-anatomy) unless handing off
- UV unwrap (→ lookdev)
- Design/silhouette still unlocked (→ character-design first)

## Instructions

1. Refuse to model without a sheet (or at least a locked silhouette) and a scale master.
2. Choose workflow (decision 5.3).
3. Organic (D17): box/subdiv, curvature-driven, Subdivision Surface modifier. Quads.
4. Hard-surface (D18): blockout → Bevel (weight-based) → booleans → weighted normals → apply late. Sharp edges with bevel logic, not raw ngons.
5. Character (D19): import turnaround as background images; real scale. Start from primitive, base mesh (D135), or sculpt. Body-part topology regions from Ch 31 atlas.
6. Creature (D20): driven by spec sheet. Silhouette-to-mass primitives first.
7. Topology rules (D24):
   - Quads are the unit.
   - Edge loops follow deformation (joints, face loops).
   - Poles (E3/E5) placed in stable regions, not on a bending equator.
   - Density where it deforms and where the camera sees it.
   - Non-manifold = error.
8. Retopo (D23): shrinkwrap/snap to sculpt; deformation-friendly cage; decimate sculpt only for viewport, not as the cage.
9. Bend tests before lookdev: squat, reach, twist, look-back. If it breaks, fix topology here.
10. LOD plan for backgrounds (Ch 26 / D24).
11. Apply transforms. Freeze proportions.

## Procedures

### Character modeling → Body parts → Topology regions
Use Depth 31 joint-by-joint and facial topology atlases (vertex counts, pole/transition patterns, density budgets).

### Hard-surface workflow → Modifier stack → Result
Mirror → Booleans → Bevel → Weighted Normal → (optional) Subdiv. Keep stack live as long as possible.

### Retopo
Prep (decimate display) → wrap new quads → project → apply shrinkwrap → check loops at joints → bend test.

## Decision Logic

- Film realistic hero → sculpt-first then retopo.
- Stylized boxy → box+subdiv, maybe skip sculpt.
- If deformation fails later: return here, do not "fix in weights."

## Inputs

- Character sheet / creature spec / design lock
- Scale master, poly budget
- Optional high-poly sculpt from sculpting-anatomy

## Outputs

- Deformation-ready mesh(es)
- Topology notes / LOD plan
- Bend-test results
- Shared state: asset model status; lock.model when approved

## Tools

Blender Edit Mode, modifiers (Mirror, Subdiv, Boolean, Bevel, Shrinkwrap, Decimate), optional RetopoFlow/Quad Remesher (learn system first). Ch 31 atlas. S-09 hard-surface supplement.

## Constraints

No merged props-into-character. No ngons on deforming surfaces. No unapplied scale. No modeling without scale master.

## Edge Cases

- Mechanical creature: hard-surface body + organic membranes (split objects).
- Base mesh (D135/Rigify) is legal; still retarget topology to the sheet.
- Scans: retopo, do not animate the scan.

## Failure Modes & Fixes

| MIST | FIX |
|---|---|
| Candy-wrapper joints | Add loops; fix poles; then weights |
| Tris/ngons on face | Quad the deforming regions |
| Retopo too dense | Budget table Ch 31.4 |
| Boolean mess applied early | Rebuild live stack |
| Creature mush | Return to spec + anatomy landmarks |

## Dependencies

- Needs `character-design` and `blender-foundations`
- ⇄ `sculpting-anatomy`
- Drives `lookdev` and `rigging`
- Feedback from `rigging` / `animation`

## Related Skills

sculpting-anatomy, lookdev, rigging, character-design, costume-groom

## Delegation Rules

- Anatomy landmarks / brush sculpt → `sculpting-anatomy`
- UVs → `lookdev`
- Armor plates as hard-surface stay here; garment sim mesh → `costume-groom`

## Examples

- Stylized hero: box torso/limbs, subdiv 2, face loops from atlas, 16–24 eye ring, bend test squat.
- Mech: boolean kit, bevel weights, no subdiv on sharp panels, separate moving parts.

## Required Knowledge / Context

- `knowledge/domains/ch03-modeling.md`
- `knowledge/depth/ch31-topology-depth.md`
- `knowledge/system/02d-depth-supplements.md` (S-09)

## References to Shared Resources

- `workflows/character-pipeline.md`
- `decision-engine` 5.3, 5.16
