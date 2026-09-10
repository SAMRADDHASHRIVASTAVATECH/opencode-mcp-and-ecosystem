---
name: sculpting-anatomy
description: Anatomy and proportion libraries plus sculpting craft — primary/secondary/tertiary forms, brushes, dyntopo/voxel/multires, detail transfer — so characters and creatures read as functional.
system: BAKG
version: 2.0.0
status: production
group: geometry
domains: [D21, D22]
knowledge:
  - knowledge/domains/ch03-modeling.md
  - knowledge/depth/ch16-anatomy-proportions.md
  - knowledge/depth/ch30-sculpting-depth.md
---

# sculpting-anatomy

## Purpose

Give every body (human, stylized, quadruped, avian, insect, aquatic, limbless, invented) structural logic and then sculpt it through the three-form hierarchy. Stylized art still needs simplified anatomy — caricature is anatomy with exaggeration.

## Scope

D21 Anatomy [SIT], D22 Sculpting [SIT], Depth 16 libraries, Depth 30 brush/workflow masterclass. Retopo is `modeling`.

## Activation Conditions

- User asks about proportions, muscles, joint ranges, sculpting, brushes, dyntopo, multires, alphas, face sets
- Creature/human needs structural logic
- `Use sculpting-anatomy`

## Non-Activation Conditions

- Building the animation cage (→ modeling retopo)
- Texture/pore maps as lookdev (pores may be sculpted then baked — bake is lookdev)
- Design silhouette still unlocked (→ character-design)

## Instructions

1. Pull numbers from Depth 16 before sculpting: human table, body-type spectra, stylized archetypes, head/face systems, joint ranges, muscle forms, quadruped/avian/insect/aquatic/limbless, invented toolkit.
2. Landmarks first (visible bones): ASIS, greater trochanter, olecranon, acromion, zygomatic, mastoid, etc.
3. Sculpt three-form hierarchy:
   1. Primary forms — big masses (gesture, proportion). Gate.
   2. Secondary — muscles, pads, folds. Gate.
   3. Tertiary — pores, wrinkles, scales. Only after primary/secondary approved.
4. Topology strategy: dyntopo for exploration, voxel remesh for even density, multires for detail on a locked base.
5. Region order (head example): skull mass → brow ridge → zygomatic → jaw → sockets → nose → lips → ears → secondary → tertiary.
6. Detail transfer: bake path is lookdev (D28); keep a high-poly archive.
7. Gate: high-poly approved → retopology (`modeling`).

## Procedures

### Invented creature toolkit (16.12)
Combine locomotion class + mass + joint scheme from existing libraries. Do not invent physics. Attach real joint ranges, then exaggerate.

### Brush encyclopedia
Use Depth 30: Clay/Clay Strips for mass, Crease for lines, Smooth as a partner not a crutch, Grab for proportions, Inflate/Blob carefully, Mask + Face Sets for regions. F size, Shift-F strength, Ctrl invert, Shift smooth.

### Time budgets
Primary 40%, secondary 40%, tertiary 20%. Most failed sculpts spent the budget on pores.

## Decision Logic

- Realistic film human → anatomy mandatory.
- Stylized → simplified anatomy still mandatory.
- Skip sculpt for hard-surface-only assets.
- If proportion is wrong, Grab at primary — never add tertiary to hide it.

## Inputs

- Sheet / creature spec / proportion target
- Style (realistic vs stylized exaggeration)

## Outputs

- High-poly sculpt
- Anatomy notes (landmarks, ranges used)
- Form-gate approvals
- Hand-off to modeling for retopo
- Shared state: sculpt approved?

## Tools

Sculpt Mode, dyntopo, voxel remesh, multires, custom alphas, tablet recommended. Depth 16 & 30.

## Constraints

Do not animate dyntopo. Do not skip primary. Do not sculpt at final density from minute one.

## Edge Cases

- Multi-species hybrid: pick a dominant locomotion skeleton, graft extras as functional or decorative.
- Stylized over-muscled hero: still obey joint ranges or the rig will break.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Mush creature | Landmarks + spec sheet |
| Smeared sculpt | Brush settings (30.2); lower strength; draw on forms |
| Detail on wrong proportion | Step back to primary Grab |
| Viewport death | Remesh strategy; hide levels |

## Dependencies

- Consumes `character-design`
- ⇄ `modeling` (retopo / cage)
- Informs `rigging` (joint ranges) and `animation` (believable motion)

## Related Skills

modeling, character-design, rigging, lookdev

## Delegation Rules

- Retopo/topology atlas application → `modeling`
- Pore maps / bake → `lookdev`
- Joint placement in armature → `rigging` (but ranges come from here)

## Examples

- Adult heroic: 8.5 heads, V-torso, joint ranges from 16.5, sculpt primary masses 2 hours, secondary muscles, tertiary only on face/hands.
- Insectoid: 16.9 anatomy, chitin plates as secondary forms, legs as exoskeleton segments.

## Required Knowledge / Context

- `knowledge/domains/ch03-modeling.md` (D21 D22)
- `knowledge/depth/ch16-anatomy-proportions.md`
- `knowledge/depth/ch30-sculpting-depth.md`

## References to Shared Resources

- `workflows/creature-pipeline.md`
- `templates/creature-spec.md`
