---
name: hybrid-eps-master
description: Analyze raster edges and create verified hybrid/vector EPS, SVG, PDF, or PNG through the Hybrid EPS MCP.
---
# Hybrid EPS Master

Use the MCP strategically; never guess image suitability or write before approval.

1. `eps_get_capabilities`: begin here to confirm algorithms, versions, formats, root and limits.
2. `eps_inspect_image(path)`: validate source and inspect format, dimensions, frames, alpha, ICC/EXIF presence, bytes and SHA-256.
3. `eps_compare_methods(path, methods, base_edge_settings)`: compare edge density, connected components, contours and vertices across Canny/Sobel/Laplacian/Scharr. Use Canny for clean linked boundaries; Scharr/Sobel for gradients; Laplacian cautiously on low-noise sources.
4. `eps_analyze_edges(path, edge_settings, vector_settings)`: estimate complexity before writing. High density/vertex count means noisy or huge output; raise blur/min-area/simplification or use morphology.
5. `eps_validate_settings(...)`: normalize and strictly validate the three settings objects.
6. `eps_list_presets`: starting points only, not universal answers.
7. `eps_get_algorithm_guidance`: consult method and output semantics.
8. `eps_plan_export(...)`: creates an exact non-writing plan for one output, including overwrite risk.
9. `eps_plan_batch(...)`: same for up to 1000 inputs; inspect every collision.
10. Explain input/output, format, layers, detector, complexity, overwrite and resource impact. Obtain explicit user approval.
11. `eps_approve(plan_id,"approve")`, then immediately `eps_execute(plan_id,token)`; tokens expire in 60 seconds and are single-use.
12. `eps_get_job(job_id)` until completed/failed/cancelled. Success requires `verified=true`, output size and SHA-256. Use `eps_cancel_job(job_id,"CANCEL")` only on explicit cancellation.

Settings:
- Edge: `method`, Canny thresholds, odd `blur_kernel`, optional morphology and odd kernel, invert.
- Vector: contour retrieval, minimum area, Douglas–Peucker `simplify_epsilon`, maximum contours.
- Export: 72–1200 DPI, `#RRGGBB`, positive edge width, bitmap/vector layer toggles, format, transparency.

Choose SVG for explicit inspectable paths and optional embedded PNG. Choose EPS for legacy print workflows but expect limited transparency. PDF is a practical hybrid interchange format. PNG is raster-only final rendering even when generated from paths.

Error recovery: path errors mean use a path beneath configured root; kernel errors require odd values; extension must match format; empty/flat images may legitimately produce zero contours; noisy output calls for more blur, morphology close/open, larger min area or simplification. Never describe contour tracing as semantic object recognition, OCR, font recovery, Bezier reconstruction, or full color-region vectorization.
