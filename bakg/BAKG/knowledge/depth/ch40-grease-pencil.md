# Depth Chapter 40 — Grease Pencil & Hybrid 2D-3D Depth

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 226–228 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 40 — GREASE PENCIL &
HYBRID 2D-3D DEPTH
Expands D130. The complete 2D-in-Blender craft: GP3 object model, strokes & materials, drawing/
animation  workflow,  onion  skin,  effects,  and  the  hybrid  2D-3D  pipelines  (boards,  animatics,  2D
characters in 3D worlds, 3D characters with 2D effects).
40.1 THE GREASE PENCIL OBJECT MODEL (GP3, Blender
4.3+)
GP object: contains layers (drawing levels) and frames (per layer); strokes live in frames.
Layers stack like Photoshop layers; frames are the animation timeline (each layer animates
independently).
Strokes: points with position, pressure, and vertex colors; strokes have material (stroke/fill)
assigned per stroke.
Materials: GP materials define stroke color/opacity and fill (with gradient/pattern options) — 
multiple materials per object let you draw in layers of color.
Modifiers (GP): the GP modifier stack (noise, simplify, smooth, outline, thickness, tint, mirror,
envelope…) — the "post-process" of strokes.
Grease Pencil 3 (4.3+): rewritten renderer/material system; strokes render through EEVEE/
Cycles; vertex-color painting on strokes.
40.2 DRAWING & ANIMATION WORKFLOW
Setup: draw on a GP object in the 3D viewport (draw mode); use the 3D cursor plane or draw
on a surface (align to a plane/mesh).
Stroke tools (Dope Sheet/GP toolbar): Draw (freehand), Line, Arc, Box, Circle, Fill (auto-close
+ fill), Erase, Eyedropper; pressure (tablet) for line weight.
Frames & onion skin: new frame per drawing; onion skin (previous/next ghosting) — the 2D
animation standard; adjust ghost opacity/count.
Animation: keyframe strokes per layer (GP frames ARE the keys); use interpolate strokes (auto
in-betweening between two key drawings — rough but a time-saver for simple motions); or draw
every frame (classic 2D).
Layers discipline: background / character / foreground / FX as separate GP layers (or objects) —
for easy edits and renders.
• 
• 
• 
• 
• 
1. 
2. 
3. 
4. 
5. 
DEPTH CHAPTER 40 — GREASE PENCIL & HYBRID 2D-3D DEPTH

40.3 GP MATERIALS & LOOKS (making it look like 2D, not
3D)
Look Recipe
Clean cartoon black stroke material + flat fill material; EEVEE render, no AA issues
Watercolor-ish low-opacity strokes, soft fills, blur/paper texture in comp (Ch 36)
Pencil sketch single material, pressure-based opacity, noise modifier
Ink lineart thick black strokes, no fill; background white/paper
Anime-style black outline + flat fills with limited palette (Ch 18)
T exture strokes use texture in the GP material (stroke texture: paper, chalk)
3D-2D hybrid GP strokes on 3D surfaces (drawn on a mesh) — "2D in 3D space"
The GP render pipeline: EEVEE (fast, crisp strokes, real-time); Cycles renders GP too (as geometry
— heavier); for film, render GP as a separate pass (over/under the 3D) and composite (Ch 36).
40.4 2D ANIMATION IN GP (the classic workflow inside
Blender)
Key poses → extremes → in-betweens: draw the key frames, the extremes, then in-betweens
(with onion skin); straight-ahead for action/fluid lines.
Timing (Ch 29.3): 2D timing is the same as 3D — the tables apply (blink 2–4, walk 12–16/
step…).
Cleanup & tie-down: rough pass → clean pass (new layer) → color pass.
The tools: stroke sculpt (edit strokes), stroke fill (fill enclosed areas), interpolate for rough in-
betweens, duplicate frame for holds.
When GP 2D is right: storyboards/animatics (D09/D10), 2D characters, hand-drawn FX overlays,
stylized full-2D films; when not: photoreal 3D pipelines (the 3D systems win).
40.5 THE HYBRID 2D-3D PIPELINES (the powerful
combos)
Hybrid How Use
3D world + 2D
characters
GP characters in a 3D scene (drawn on planes, animated in
GP)
stylized films, storybook
looks
2D world + 3D
characters
GP background (painted) + 3D character rendered, comped
together
the "3D in 2D" look
3D characters + 2D
effects
GP FX overlays (speed lines, impact stars, motion lines —
D100/D101 stylized)
anime/cartoon effects (Ch
18/35)
2D boards + 3D
previs
GP boards in 3D space (D11/D38.6) storyboarding/staging tests
3D base + GP detail GP strokes on 3D surfaces (projected) stylized detail, line art on
3D
GP cleanup overlays GP redlines over 3D renders (review) art direction, notes (D127)
• 
• 
• 
• 
• 
DEPTH CHAPTER 40 — GREASE PENCIL & HYBRID 2D-3D DEPTH

The comp rule: hybrids live or die in compositing (Ch 36) — render GP and 3D as separate passes
with matching color management (AgX, D112) and grade them together; the "2D/3D disconnect" is
almost always a color/lighting mismatch, not a stroke problem.
40.6 GP PERFORMANCE & OPTIMIZATION
Stroke counts: GP is geometry; tens of thousands of strokes = heavy — simplify strokes
(modifier: Simplify/Adaptive) and keep stroke density sane.
Viewport: GP renders fast in EEVEE; keep the viewport at reasonable stroke counts while working
(display limits).
Onion skin cost: few ghosts, low opacity.
Rendering: EEVEE final (fast) or Cycles (if GP must match 3D lighting); GP as a separate pass
in comp is the performance + flexibility standard.
40.7 GP FAILURE MODES & FIXES
Symptom Cause Fix
Strokes flicker/AA artifacts thin strokes + low res thicken strokes, render 2× downscale, EEVEE
AA
Fill doesn't close open stroke loop close the loop, use auto-fill, adjust fill tolerance
2D-3D disconnect color/light mismatch grade both passes together (Ch 36)
GP slows down too many strokes simplify modifier + stroke budget
Onion skin confusing too many ghosts fewer ghosts, lower opacity
Strokes move with camera
unexpectedly
drawn on wrong plane draw on a fixed plane / lock plane
Can't animate easily no layer/frame
discipline
one layer per element, keyframes per layer
• 
• 
• 
• 
DEPTH CHAPTER 40 — GREASE PENCIL & HYBRID 2D-3D DEPTH
