# Validation & the final report

## Automatic checks
The skill verifies as many of these as its tools allow (file checks run with
`trimesh` when present; the rest are reported by the Blender script):

- mesh exists
- mesh is not empty
- geometry parses / loads
- normals valid (no degenerate/flipped catastrophe)
- polygon count is reasonable and non-zero
- textures present when expected
- materials assigned
- armature exists when rigging was requested
- weights exist when rigging was requested
- exported file exists

Because it cannot open a GUI here, "model opens correctly in Blender" is handled
by the Blender headless run itself (it imports and processes the mesh; success
implies Blender opened and manipulated it). The exported file existence is
confirmed on disk.

Validation is **all-or-nothing honest**: if any expected check fails, the project
is not marked validated and the report lists the failing checks.

## Final report
Written to `<project>/report.md` (human) and `<project>/report.json` (machine),
covering:

- source image
- reconstruction method (+ kind)
- generated files
- polygon count
- texture resolution
- number of objects
- armature status
- facial rig status
- export formats
- warnings/errors
- recommended next steps

## Export
- Prefer **GLB/GLTF** for general real-time use.
- Prefer **FBX** when an animation/game-engine workflow requires it.
- **OBJ** on request.
- **STL** only when explicitly requested — never for animated characters by
  default.
