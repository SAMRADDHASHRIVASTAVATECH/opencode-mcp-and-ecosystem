# Depth Chapter 19 — Shape Keys, Blendshapes & Driver Automation

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 154–156 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 19 — SHAPE KEYS,
BLENDSHAPES & DRIVER AUTOMATION
Expands D59, D60, D54, D58. The machinery of morphable surfaces and automatic control: shape-
key  system  mastery,  the  60+  facial  blendshape  library,  and  the  driver  language  with  a  dozen
production recipes.
19.1 SHAPE KEY SYSTEM MASTERY (Blender)
Fundamentals: - A shape key stores a vertex displacement from the Basis. Shape keys are per-
mesh; multiple meshes (body, face, hands) have separate shape key lists. - Relative keys (default):
each key is a delta from Basis, with value 0–1 (can go negative/above 1). Absolute keys (rare): each
key is a full pose, interpolated by index. - Value & range: value (the animation channel) vs Min/Max
(allowed range — clamp to avoid breaking the mesh);  interpolation default Linear; set "Vertex
Group" on a key to limit its influence to a region (e.g., only the mouth region). - In-between keys:
shape keys can have "in-between" states at value ranges (the range slider) — used for multi-stage
morphs (jaw open 0–0.5–1.0 stages). - Basis editing: to fix the whole mesh, edit the Basis; to fix one
pose, edit that key. - Keying: animate shape key values in the Dope Sheet (keyed like any property);
driven by bones via drivers (19.3) for facial rigs (D60).
Corrective workflow (D59, expanded):  (1) create Basis; (2) pose the armature at the problem
angle; (3) add a shape key ("Fix_Elbow90"); (4) with the mesh in that pose , edit vertices to fix the
deformation; (5) set value 0; (6) driver: elbow bone rotation → key value (smooth on/off via the driver
curve — no pops). For two-bone combinations (e.g., twist + bend), use two drivers multiplied or a 2-
axis driven key with an "in-between" for the corner case.
Mistakes: editing the wrong key (verts permanently displaced); keys that move verts they shouldn't
(explosions); range not clamped (mesh inverts); drivers with hard 0↔1 jumps (popping).
19.2 THE FACIAL BLENDSHAPE LIBRARY (60+ keys for a
production face rig)
Structure — organize into groups for drivers and pose library (D64):
Jaw  &  mouth  (the  phoneme/expression  workhorse):  Jaw_Open,  Jaw_Side,  Jaw_Forward,
Lip_Upper_Center_Up,  Lip_Upper_L_Corner_Up,  Lip_Upper_R_Corner_Up,  Lip_Lower_Center_Down,
Lip_Lower_L_Down,  Lip_Lower_R_Down,  Lip_Corner_L_Out  (smile),  Lip_Corner_L_In  (sneer/pucker),
Lip_Corner_R_Out,  Lip_Corner_R_In,  Lip_Pucker,  Lip_Funnel  (O),  Lip_Stretch  (wide),  Lip_Tight,
Lip_Flatten, Mouth_Open_Big, Mouth_Open_Small, Smile_Open (teeth), Smile_Closed, Frown, Sneer_L,
Sneer_R, Lower_Lip_Out (pout).
Brows & forehead (emotion drivers): Brow_Inner_Up_L/R (sad/worried), Brow_Outer_Up_L/R (surprise),
Brow_Down_L/R (angry), Brow_Squeeze (focus), Forehead_Wrinkle.
Eyelids  &  eyes  (the  life  system):  Eye_Blink_L/R,  Eye_Squint_L/R,  Eye_Wide_L/R,
Eye_Upper_Lid_Down_L/R, Eye_Lower_Lid_Up_L/R, Eye_Dart (whole-eye shape keys rarely needed —
use rig bones D63), Eye_Brow_Up_L/R (brow+lid combo).
DEPTH CHAPTER 19 — SHAPE KEYS, BLENDSHAPES & DRIVER AUTOMATION

Cheeks, nose, ears:  Cheek_Raise_L/R (smile), Cheek_Puff, Cheek_Suck, Nose_Wrinkle, Nose_Flare,
Ear_Wiggle.
T ongue (if shape-based): T ongue_Out, T ongue_Up, T ongue_Side.
Viseme set (lip sync, D62) as shape keys:  AH, EE, IH, OH, OO, MM (closed), FF (teeth-lip), TH, LL
(tongue  up),  SHH  (pucker),  SS  (teeth),  NGK  (open  back),  QQ/WW  (round),  REST.  ~12–15  keys;
everything else is jaw + blends.
Body morph library (the character system):  Height_Up/Down, Width_Up (fat), Muscle_Up/Down,
Bust, Hips, Belly, Shoulder_Width, Neck_Thick, Arm/Thigh_Girth — a parameterized body (used by
base-mesh systems and GN characters, Ch 20).
19.3 THE DRIVER LANGUAGE (Blender, practical)
Driver anatomy: a property gets its value from an expression over variables (which reference other
properties).
Variable types: Single Property (bone transform, object transform, custom property, shape key,
scene property…); Transform Channel (a bone's local/world location/rotation/scale — with space
settings); Rotational Difference (angle between two bones — great for joint drivers).
Expression syntax: Python-like: var * 2 , clamp(var, 0, 1) , max(var1, var2) , var1 + var2 , 
round() , sin(frame * 0.1) , frame  (current frame — time-based animation for free), pi .
Driven sources: bones (pose space), custom properties (the interface — put them on the rig
root: Properties → Custom Properties ), shape keys, shader values, node values, scene properties
(global "wetness", "wind" — D99).
Driver on F-curve: a driver can also be an F-curve (the driver editor's curve view) — smoother
control than raw expressions for complex response curves (e.g., elbow bend → wrinkle with
easing).
Evaluation & debug: drivers evaluate continuously (real-time); a purple value = error (broken
variable path — re-target the variable); driver editor shows the expression and values. Keep
expressions simple; complex logic belongs in a script (Ch 24).
19.4 TWELVE PRODUCTION DRIVER RECIPES
IK/FK switch: custom property IK_FK_Arm  (0–1) on the rig root → two constraints' Influence (IK
constraint influence = prop; FK controls' influence = 1 − prop, or FK control visibility). Standard
limb control.
Blink automation: Blink  custom property on the face control → eyelid shape keys: Blink_L =
clamp(Blink,0,1) , Blink_R = clamp(Blink,0,1) ; animator keys the property; a blink cycle can be a 
noise driver: 0.5 + 0.5 * sin(frame * 0.8)  + random-ish via hash(frame)  — but for acting, key
manually (D63).
Brow follow: brow shape keys driven by a brow control bone's local Z location: 
clamp(L_Brow_Ctrl.location.z * 2, -1, 1)  — one bone drives multiple brow keys with different
weights.
Jaw + lips: jaw bone rotation → Jaw_Open shape key (with easing curve); lips follow the jaw with
a fraction (0.3) for natural lag.
Auto-clavicle: shoulder bone rotation → clavicle bone rotation × 0.3 (the scapula slide, D16/28).
Bone-driven, so it inherits.
Breathing: chest scale Z driven by 0.985 + 0.015 * sin(frame * 0.6)  — subtle, looped; pause
breathing on held breaths (key the scale manually for acting).
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
6. 
DEPTH CHAPTER 19 — SHAPE KEYS, BLENDSHAPES & DRIVER AUTOMATION

Stretch system: global Stretch  property → each bone's scale = 1 + Stretch *
stretch_factor(bone) ; IK stretch via Stretch T o constraint influence.
Mechanical piston: piston bone location X driven by var  = crankshaft bone rotation → 
sin(crank.rotation_euler.z) * stroke + offset  — classic crank-piston.
Gear linkage: gear bone rotation = driver_bone.rotation_euler.z * -2  (ratio + direction) — drive
whole chains.
Wetness (shader): object custom property Wetness  → roughness Mix factors + coat + BC darken
(Ch 17 recipe 6) — one slider wets materials, driven by rain system (D99).
Wing flap automation: wing bone rotation = sin(frame * freq) * amplitude  for preview; final =
hand-keyed (drivers preview, keys final).
Look-at blend: head bone's Track T o influence driven by Look_Amount  (0–1) — blends head-look
between FK and gaze-target.
19.5 SHAPE KEY & DRIVER FAILURE MODES
Symptom Cause Fix
Mesh explodes at a
pose
Key edits wrong verts / range
unclamped
Reset key, re-edit localized; clamp Min/Max
Popping morphs Driver curve hard 0↔1 Use eased driver curve (F-curve view), 3–5
frame blend
Purple driver value Broken variable path (renames) Re-target variables; rename before deleting
bones
Keys fighting the
armature
Editing keys with rig posed wrong Edit in rest pose + only the posed corrective
keys per D59
Shape keys not
animating
Key not selected in Dope Sheet / wrong
channel
Check the shape key's "Value" channel is keyed
Performance Hundreds of driven keys per frame Bake drivers to keys for final (D54); keep driven
set minimal
Inconsistent facial
response
Asymmetric drivers Mirror driver setups; test both sides
7. 
8. 
9. 
10. 
11. 
12. 
DEPTH CHAPTER 19 — SHAPE KEYS, BLENDSHAPES & DRIVER AUTOMATION
