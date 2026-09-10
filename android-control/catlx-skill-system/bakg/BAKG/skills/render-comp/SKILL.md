---
name: render-comp
description: Rendering, engine choice execution, optimization, passes/AOVs, compositing, color correction and grading — turning the scene into film images without re-rendering to fix color.
system: BAKG
version: 2.0.0
status: production
group: image
domains: [D112, D113, D114, D115, D116, D117, D118, D119, D136]
knowledge:
  - knowledge/domains/ch14-render-comp.md
  - knowledge/depth/ch36-compositing-color.md
  - knowledge/system/02d-depth-supplements.md
  - knowledge/depth/ch24-pipeline-automation.md
---

# render-comp

## Purpose

Compute images (Cycles/EEVEE/Workbench), split them into controllable passes, assemble them into film, correct then grade. Render once, grade twice.

## Scope

D112–D119, D136 farms, Depth 36, S-13 cheat sheet, farm notes in Depth 24.5. Final encode/delivery is `production-finishing` but this skill produces EXR masters.

## Activation Conditions

- Samples, denoise, Cycles, EEVEE, EXR, passes, Cryptomatte, compositor, grade, LUT, AgX, render farm
- `Use render-comp`

## Non-Activation Conditions

- Designing lights (→ lighting)
- Designing materials (→ lookdev)
- Final codec for YouTube (→ production-finishing) after grade

## Instructions

1. Engine already committed (5.2). If not, resolve it.
2. Color management: AgX default. Exposure per scene. Don't "fix" with RGB curves on the raw combined only — use passes.
3. Output: EXR multilayer frames, never final-to-compressed-video from the 3D file (D128).
4. Iterate at 25–50% res, low samples + denoise; final 100% after approval. Never iterate at final settings (S-13).
5. Cycles: 32–128 samples + OIDN/OptiX denoise; adaptive sampling ON; bounces 4–8; caustics OFF unless needed; GPU.
6. EEVEE Next (4.2+): raytracing options in Ch 25; still commit look.
7. Optimization order (D114): denoise → lights/samples → bounces → shader complexity → volumes → geometry.
8. Passes (D115): Combined, Diffuse, Glossy, Transmission, Volume, Emit, Env, AO, Mist, Shadow, Cryptomatte. Enable what comp will use.
9. AOVs (D116): wetness, magic, custom. Cryptomatte for isolations.
10. Compositor cookbook (36.1): Render Layers → premult → grade tree → glows → DoF/MB if not rendered → grain → output.
11. Pass-based relighting (36.2) instead of re-render when possible.
12. Color correction (D118) first (exposure, WB, contrast) then grading (D119) look. Scopes (36.3). Shot → sequence → film (36.4).
13. Film looks/LUTs (36.5). Stylized grading matches shading (36.6 / Ch 18).
14. Farms (D136): Flamenco; crash-safe frames; re-render failed only.
15. Motion blur 2–8% shutter if rendered; else vector blur (5.7).

## Procedures

### Cheat sheet (S-13)
Samples 32–128 + denoise; AgX; EXR multilayer; WIP 25–50%; GPU on.

### Comp integration of VFX
Additive/screen glows on emission/AOV; grain after; match plate if D132.

### When image is wrong
If noise/fireflies: samples/clamp/shader. If mood wrong: lighting. If color wrong: this skill. If albedo wrong: lookdev. Don't re-render to warm a shot 200K.

## Decision Logic

5.2 engine, 5.7 DoF/MB, 5.8 format, 5.15 offline vs realtime. PBR-pure materials allow hybrid EEVEE iterate / Cycles hero.

## Inputs

- Lit scene, style, shot camera, required passes, farm or local, budgets

## Outputs

- EXR sequences
- Comp .blend or node tree
- Grade notes / LUT
- Test frames approved
- Shared state: shot rendered/comped; `locks.render`

## Tools

Cycles, EEVEE, Workbench, Compositor, Cryptomatte, OIDN/OptiX, Flamenco, FFmpeg later. S-13, Ch 36, Ch 25 for EEVEE.

## Constraints

Never ship JPEG as master. Never skip denoise strategy. Never grade before correct. Never change AgX mid-film without a reason.

## Edge Cases

- Toon: separate character/world ramps; grade together (18.7).
- Volumes + crystals: Cycles, cap transmission/volume bounces.
- Realtime film: EEVEE settings from Ch 25.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Noise | Denoise; more samples on volumes; clamp |
| Fireflies | Roughness min; clamp indirect; caustics off |
| Banding | EXR; dither; grain |
| Flicker denoise | More samples; temporal; don't mix denoisers |
| Looks different per shot | 36.4 sequence grade; scopes |
| Black frames | Missing textures/overrides; farm path |

## Dependencies

- Needs lighting + lookdev
- Consumes vfx layers
- Drives production-finishing edit
- Feedback to lighting/lookdev

## Related Skills

lighting, lookdev, vfx, production-finishing, cinematography, decision-engine

## Delegation Rules

- Mood not working → lighting
- Plastic skin in render → lookdev
- Encode/loudness/delivery → production-finishing
- Python batch render → production-finishing Ch 24

## Examples

- Short film: Cycles 64 adaptive + OIDN, EXR multilayer, mist+crypto, comp grain + mild LUT, ProRes from VSE later.
- Stylized: EEVEE, Shader-to-RGB already in lookdev, comp outlines if line-art, punchy grade.

## Required Knowledge / Context

- `knowledge/domains/ch14-render-comp.md`
- `knowledge/depth/ch36-compositing-color.md`
- S-13 cheat sheet
- `knowledge/depth/ch24-pipeline-automation.md` (farms)
- `knowledge/depth/ch25-realtime.md` (EEVEE)

## References to Shared Resources

- `decision-engine` 5.2 5.7 5.8 5.15
- `workflows/shot-pipeline.md`
