# Rigging

Run inside the Blender script when `--rig` is passed.

## Humanoid armature
A bone chain is created with names: `pelvis`, `spine`, `chest`, `neck`, `head`,
plus limbs `upper_arm_L/R`, `lower_arm_L/R`, `hand_L/R`, `thigh_L/R`,
`shin_L/R`, `foot_L/R`. Automatic weights (`ARMATURE_AUTO`) skin the character
mesh. Basic IK is added on the leg bones with `IK_target_L/R` empty controls.

The skeleton is laid out along the character's up axis inside the normalised
mesh, so a game-engine humanoid retarget is a reasonable next step.

## Facial controls
For anime characters the skill attempts basic facial/expression control:

- If the mesh already has separate geometry or shape keys, it reports that
  advanced binding to eye/mouth bones is available to wire up.
- Otherwise it adds a `Basis` shape-key set and creates blending foundations, and
  **clearly reports** that eye/mouth *bone* controls need the separate eye/mouth
  meshes. It never claims a full facial rig exists when it does not.

Because a single merged reconstruction rarely contains separate eye/mouth meshes,
the facial stage commonly reports `blendshapes_added` + a note that binding eye
and mouth bones is manual. That is reported honestly in the final report's
`facial_rig_status`.

## Manual-rig fallback
If automatic rigging fails, the skill **preserves the clean mesh** (already
normalised/cleaned/exported where possible) and reports `armature: false` with a
reason and a clear manual-rig fallback: open the project `.blend`/mesh in
Blender, add an armature, and parent with automatic weights. The final report
marks the model as not animation-ready until rigging is validated.

## Validation truth
The model is reported animation-ready only if validation observed: mesh exists,
armature exists, weights exist, and exports succeeded. Otherwise the report says
exactly which part is missing. See validation.md.
