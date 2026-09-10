# Dependency Order

## Edge types (Part 3)

| Edge | Meaning | Example |
|---|---|---|
| → NEEDS | A cannot be done properly without B | Rigging NEEDS Topology |
| → DRIVES | A produces the input for B | Character Design DRIVES Modeling |
| → AFFECTS | A changes the quality/cost of B | Model Complexity AFFECTS Render Cost |
| → CONSTRAINS | A sets limits B must respect | Story CONSTRAINS Shot Design |
| ⇄ FEEDBACK | B's result should loop back to A | Animation ⇄ Rig |

## Main pipeline spine

```
IDEA → Story (D01) → Worldbuilding (D02) → Character Concept (D03) → Design (D04/D05)
→ References (D07) → Character Sheets (D08) → Storyboard (D09) → Animatic (D10)
→ Previs (D11) → 3D Planning (D14) → Blockout (D16) → Modeling (D17–D20)
→ Topology (D24) → UV (D25) → Textures (D26–D29) → Materials (D30–D36)
→ Clothing/Groom (D37–D47) → Rigging (D48–D63) → Animation (D64–D78)
→ Environment (D79–D86) → Physics/VFX (D87–D101)
→ Camera (D102–D107) → Lighting (D108–D111)
→ Rendering (D112–D116) → Compositing (D117–D119)
→ Editing (D120) → QC (D127) → Final Output (D128) → Archive (D129)
```

## Critical edge sets

### Chain 1 — Design → Geometry → Deformation (the character spine)

Design (D04/D05) DRIVES Modeling (D19/D20) NEEDS Anatomy (D21)
→ Sculpt (D22) → Retopo (D23) NEEDS Topology (D24)
→ Rigging (D48) NEEDS Skinning (D57) → Deformation (D58)
⇄ Animation (D64)

If deformation fails: fix topology, not weights.

### Chain 2 — Performance → Secondary Motion → Simulation

Animation (D64) DRIVES Secondary (D77) DRIVES Cloth (D39/D91) / Hair (D47/D92)
NEEDS Physics infrastructure (D88). Simulate last.

### Chain 3 — Camera → Light → Render → Comp (the image chain)

Camera (D102) DRIVES Lighting (D108) AFFECTS Rendering (D112)
DRIVES Compositing (D117) DRIVES Grading (D119).

### Chain 4 — Story → Film (the meaning chain)

Story (D01) CONSTRAINS Shot Design (D106) DRIVES Boarding (D09)
DRIVES Animatic (D10) CONSTRAINS Asset list (D14) CONSTRAINS everything else.
Editing (D120) ⇄ Story.

## Skill-level order (default)

```
bakg-orchestrator / decision-engine
→ preproduction
→ character-design
→ blender-foundations
→ modeling ⇄ sculpting-anatomy
→ lookdev
→ costume-groom
→ rigging
→ animation
→ environment
→ simulation → vfx
→ cinematography → lighting
→ render-comp
→ production-finishing
```

`grease-pencil` may insert at boarding, overlay, or hybrid-shot time.

Full relationship map: `knowledge/system/03-relationship-map.md`.
