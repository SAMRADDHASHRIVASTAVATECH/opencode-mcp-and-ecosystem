# Production Economy Rules

Apply to every project. These are standing system rules, not optional advice.

1. **Decide cheap, execute expensive.** Make all look/style decisions in 2D; 3D is for execution.
2. **One rig, one render engine, one naming convention** — commit early.
3. **The asset list is set by the animatic.** Lock the shot list before modeling anything expensive.
4. **Block out everything before detailing anything.** Scale errors are the most expensive error class.
5. **Never animate a character with a non-final rig.** Test-rig at blockout, final-rig before animation.
6. **Simulate last.** Cloth/hair/fluid need final animation; they also need final-ish meshes.
7. **Render once, grade twice.** Fix color in compositing, not by re-rendering.
8. **Back up the decisions, not just the files.** Keep the animatic, character sheets, and naming docs.

## Cost of change

Cost of change grows with each stage. Changing a character's silhouette after rigging costs days; after animation, weeks. The journey is therefore a sequence of cheap, high-information decisions first (2D, still images) → medium-cost structure (blockout, layout) → expensive polish (textures, sims, final lighting).

## Feedback loops (edges that point backward)

The journey is not strictly linear. Real productions loop:

- Animatic → Storyboard (pacing broken → re-board)
- Blockout → Previs (composition fails → re-stage)
- Rig → Model (deformation fails → fix topology, not weights)
- Animation → Rig (controls unusable → rebuild controls)
- Render → Material/Lighting (noise, banding, wrong look → tune)
- QC → Any stage (final review catches everything)

Plan time for these loops. A production without review gates is a production that discovers its errors at render time.

## Fake first

Simulation vs fake rule (D88 #2): fake first. Sim only when faking is harder or visibly worse.

## Locks

Locks are promises to stop polishing; honor them. Infinite polish is the silent production killer. See decision tree 5.10.
