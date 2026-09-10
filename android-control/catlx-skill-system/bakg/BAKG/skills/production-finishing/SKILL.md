---
name: production-finishing
description: Editing, sound and music, shot/asset/file organization, versioning, pipeline, performance optimization, QC, final output, archiving, add-ons, Python/USD/export, render ops, and real-time/game export.
system: BAKG
version: 2.0.0
status: production
group: ops
domains: [D120, D121, D122, D123, D124, D125, D126, D127, D128, D129, D133, D134, D137]
knowledge:
  - knowledge/domains/ch15-production.md
  - knowledge/depth/ch23-sound-music.md
  - knowledge/depth/ch24-pipeline-automation.md
  - knowledge/depth/ch25-realtime.md
  - knowledge/depth/ch26-optimization.md
  - knowledge/system/02d-depth-supplements.md
---

# production-finishing

## Purpose

The operations layer that finishes films and keeps productions from collapsing: cut, sound, track shots, name files, version, pipeline gates, optimize, QC, deliver, archive — plus automation and realtime export when needed.

## Scope

D120–D129, D133, D134, D137, Depth 23–26, S-14 shot management, S-15 QC, S-16 archive, S-18 add-ons. Rendering *images* is `render-comp`; this skill takes EXR into the edit and out to humans.

## Activation Conditions

- Edit, VSE, sound, foley, loudness, shot tracker, folders, versioning, pipeline, QC, deliver, archive, bpy, USD, glTF, LOD, EEVEE game, add-ons
- `Use production-finishing`

## Non-Activation Conditions

- Compositing node trees for beauty (→ render-comp)
- Story structure (→ preproduction) though editing ⇄ story
- Viewport navigation basics (→ blender-foundations)

## Instructions

### Editing (D120 / Ch 21)
Cut EXR/image strips + audio in VSE (or Resolve). Pacing from animatic. Continuity rules. Don't recut to hide broken animation — flag QC.

### Sound (D133 / Ch 23)
Sound is half of film. Dialogue / foley / ambience / music. Sync to picture. Mix and loudness. VSE audio or external DAW. Horror: silence is a layer.

### Shot management (D121 / S-14)
Spreadsheet: ID, status ladder, owner, version, deps, deadline, render order. Animatic shot list is the master.

### Assets & files (D122/D123)
Asset Browser, libraries, linking, library overrides (not old proxies). Solo studio tree (5.9). Relative paths.

### Versioning (D124)
`_v01` at milestones; incremental save; backups; versions.md. Decisions archived too (animatic, sheets, naming).

### Pipeline (D125)
The graph in action. Gates scheduled. Dependency spine from Part 1.

### Optimization (D126 / Ch 26)
Ladder top-down: budgets → LOD → textures → instancing → viewport → memory/caches → render economics. Don't optimize at the bottom first.

### Realtime (D137 / Ch 25)
EEVEE Next production settings; game/web export (glTF); draw-call and texture discipline.

### Automation (Ch 24)
bpy essentials, 30-line add-on skeleton, USD, glTF/FBX/OBJ notes, Flamenco farms, version control for blends (lock files, LFS if needed). Script repetitive tasks first (24.7).

### Add-ons (D134 / S-18)
Honest catalog. Learn system first. Manifest for archive. Built-in > add-on if equal. License-check.

### QC (D127 / S-15)
Technical checklist + 3 creative questions per gate. Final watch whole film with sound. Never ship known errors.

### Output (D128)
EXR → edit → ProRes/DNxHR master; H.264/H.265 CRF 18–23 web; 9:16 transcode from master. Don't encode from viewport.

### Archive (D129 / S-16)
Masters, final blends, sources, caches-or-settings, decision record, add-on manifest, README, checksum, 2+ media.

## Procedures

### Status ladder
planned → blocked → splined → animated → sim'd → lit → rendered → comped → approved.

### Final QC watch
Whole film, final quality, in order, with sound: continuity, color match, audio sync, frame errors, emotional flow.

### Optimization ladder (26.1)
Apply top-down. Texture is the silent memory eater (26.3). 40 GB surprise = caches (26.5).

## Decision Logic

5.9 structure, 5.10 when to stop, 5.11 add-ons, 5.15 realtime, 5.8 formats. Fake vs sim is not this skill.

## Inputs

- Comped shots / EXR, animatic, naming legend, budgets, delivery specs

## Outputs

- Locked edit
- Mix
- Masters + distribution encodes
- QC report
- Archive package
- Optional: export scenes (glTF/USD), scripts
- Shared state: `locks.edit`, gates_passed, addons_manifest

## Tools

VSE, Resolve (external), FFmpeg, bpy, Flamenco, Asset Browser, git/LFS optional. Depth 23–26. S-14–S-16 S-18.

## Constraints

Relative paths. One naming legend. Don't archive only the mp4. Don't skip the final watch. Don't buy add-on soup.

## Edge Cases

- Game cutscene: export + engine lighting may replace Cycles; still QC in engine.
- Solo: this skill is still required — folders and QC are not "studio-only."

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Lost shots | S-14 spreadsheet |
| Broken links | relative paths; pack only as last resort |
| "Almost done" forever | status ladder + 5.10 |
| Can't reopen next year | add-on manifest + README + checksum |
| Laggy viewport | Ch 26 ladder |
| Loudness illegal | Ch 23 mix targets |

## Dependencies

- Consumes render-comp output
- Constrains everyone via pipeline/naming/QC
- Feedback to any skill on QC fail
- ⇄ preproduction (edit vs story)

## Related Skills

render-comp, preproduction, blender-foundations, bakg-orchestrator, all skills via QC

## Delegation Rules

- Beauty grade issues → render-comp
- Missing animation frames → animation
- Export material mismatch → lookdev + Ch 24.4
- If user asked a whole production plan → bakg-orchestrator

## Examples

- Delivery: 24 fps, 1920×1080, ProRes 422 HQ master, H.265 web, archive zip with README + hashes.
- bpy: batch rename collections to legend; batch render shot files.

## Required Knowledge / Context

- `knowledge/domains/ch15-production.md`
- `knowledge/depth/ch23-sound-music.md`
- `knowledge/depth/ch24-pipeline-automation.md`
- `knowledge/depth/ch25-realtime.md`
- `knowledge/depth/ch26-optimization.md`
- S-14 S-15 S-16 S-18

## References to Shared Resources

- `checklists/master.md`
- `checklists/qc-technical.md`
- `checklists/archive.md`
- `templates/shot-record.md`
