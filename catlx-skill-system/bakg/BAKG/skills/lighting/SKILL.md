---
name: lighting
description: Light setup and mood, shadows, atmosphere, volumetrics — time-of-day and weather tables, 12 mood recipes, portrait patterns, color theory for light, light linking.
system: BAKG
version: 2.0.0
status: production
group: image
domains: [D108, D109, D110, D111]
knowledge:
  - knowledge/domains/ch13-lighting.md
  - knowledge/depth/ch22-lighting-mood.md
---

# lighting

## Purpose

Lighting is ~50% of rendered look. It sculpts form, creates mood, and tells the audience when/where they are. Same set, different light = different film.

## Scope

D108–D111, Depth 22. Materials must already exist (`lookdev`). Camera exists (`cinematography`). Engine limits via `render-comp`.

## Activation Conditions

- Lighting, HDRI, key/fill/rim, shadows, fog, volumes, god rays, mood, time of day, IES
- `Use lighting`

## Non-Activation Conditions

- Shader authoring (→ lookdev)
- Comp fog only as a cheap aerial (this skill still specifies it)
- Render samples (→ render-comp)

## Instructions

1. 3-point as a starting grammar: key, fill, rim — then break it with intent.
2. Light types: Sun (parallel, TOD), Area (soft, windows), Point, Spot, HDRI (World), mesh lights, IES. Light linking (4.x) for control.
3. Design shadows (D109): direction, softness (size), contact, color (not pure black). Contact shadows anchor objects.
4. Atmosphere (D110): aerial perspective cheap in mist pass/comp; physical fog when weather is the story.
5. Volumetrics (D111): Principled Volume world or local cubes. Costly. Hero shafts only. Anisotropy for forward scatter.
6. Use Depth 22:
   - 22.1 time-of-day table
   - 22.2 weather lighting table
   - 22.3 twelve mood recipes (key→fill→rim ratios & temps)
   - 22.4 portrait patterns (Rembrandt, loop, split, butterfly, rim)
   - 22.5 color theory for light
   - 22.6 controls & discipline (named lights, collections, link groups)
7. Continuity across shots of the same scene.
8. Lookdev materials must be approved under this lighting, not only studio HDRI.
9. Exposure via color management (AgX) not by blowing the sun to 10000 without intent.

## Procedures

### Mood recipe
Pick the emotion → 22.3 recipe → place key angle/temp/ratio → fill → rim → practicals → volume if needed → playblast.

### Rainy city
Weather table: overcast soft sky, cool key, warm practical windows, wet specular, haze. Volumes light.

### Dawn mech
Low sun, long shadows, cold ambient, warm rim if hitting metal, mist.

### Candle crypt
Practical candle key, crushed fill, volume dust, creature only in unlit areas (story rule).

## Decision Logic

- Stylized/anime: lighting still designed but ramps clip it (coordinate lookdev 18.7).
- Volumes only if they read at shot size.
- HDRI + sun is common; don't use 20 unmanaged lights.

## Inputs

- World bible TOD/weather, cameras, materials, mood, engine

## Outputs

- Named light collections
- Mood recipe used
- Volume/atmosphere settings
- Continuity notes
- Shared state: `locks.lighting` per scene

## Tools

Lights, World, Light Linking, IES, Principled Volume, mist pass. Ch 22 tables.

## Constraints

Don't light in isolation from camera. Don't skip contact shadows. Don't leave default sun+whatever.

## Edge Cases

- Toon: fewer lights, harder shadows, explicit face shadow.
- Night exteriors: motivated practicals, not a blue blanket.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Flat | Stronger key; darker fill; rim |
| Floating | Contact shadow; AO pass |
| Wrong time | 22.1 sun angle/temp |
| Volume noise | Smaller domain; more samples via render-comp; or fake mist pass |
| Discontinuity | Shot-to-shot light lock |

## Dependencies

- After cinematography cameras
- After lookdev (iterate together)
- Drives render-comp
- Consumes environment practicals

## Related Skills

cinematography, lookdev, render-comp, environment, vfx

## Delegation Rules

- Fireflies/noise → render-comp
- Wet materials → lookdev
- Magic as light source → vfx + this skill (mesh lights)

## Examples

- 12 mood recipes: use "dread" for Example F, "hope-dawn" for Example D, "romance-rain" for city streets.
- Rembrandt portrait for a dialogue CU.

## Required Knowledge / Context

- `knowledge/domains/ch13-lighting.md`
- `knowledge/depth/ch22-lighting-mood.md`

## References to Shared Resources

- `examples/D-abandoned-mech-flood.md`
- `examples/F-horror-crypt.md`
