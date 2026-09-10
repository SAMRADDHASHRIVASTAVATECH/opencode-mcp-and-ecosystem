# Universal Artist + Universal Visual Computing — Research Report
Date: 10 September 2026

## Conclusions
Two separate user-mode MCP servers are the safest architecture. **Universal Visual Computing** owns deterministic image/vector/procedural/video/3D capability discovery and DAG execution. **Universal Artist** owns briefs, artwork state, application capability models, workflow planning, stroke trajectories, critique, correction and export orchestration. OpenCode composes both and delegates physical GUI actions to an independently authorized Windows Live Control Agent. Neither server installs drivers, hooks the kernel, injects into applications, or uses anti-cheat/DRM bypasses.

## Verified technology findings
- Windows: UI Automation is the preferred semantic UI surface; Windows Graphics Capture/DXGI are capture paths; SendInput is user-mode, subject to UIPI, and dispatch never proves success. Per-Monitor V2 DPI awareness is required for physical-pixel coordinate integrity. [Microsoft High-DPI docs; Windows Graphics Capture; SendInput]
- OpenCV 4/5 provides mature filtering, geometry, contours, registration, optical flow, tracking and DNN support. OpenCV is Apache 2; Python wheel packaging has separate MIT scripts and bundled third-party licenses.
- Pillow is lightweight and dependable for decoding, compositing, drawing, color and format conversion. NumPy is the interchange basis.
- ONNX Runtime provides CPU plus optional DirectML/CUDA execution. `onnxruntime-directml` supports current Python/Windows and is MIT; providers must be probed rather than assumed.
- Tesseract is suitable for local printed-text OCR after preprocessing; layout/scene/handwriting need optional specialized providers.
- SAM 2 is promptable image/video segmentation with streaming memory and Apache-2.0 code/weights. It is optional and GPU-heavy; no model is downloaded automatically.
- VTracer is a practical MIT color raster-to-SVG engine with CLI/Python bindings. Potrace is strong for monochrome tracing but GPL-2+ affects distribution choices.
- FFmpeg is the standard subprocess adapter for decoding, encoding, filtering and frame pipelines; builds/codecs carry varying licenses.
- Blender officially supports background CLI and Python (`bpy`), with argument order significant. It is an adapter, not a Python dependency.
- Krita exposes a Python/libkis plugin API inside Krita for documents, nodes, filters and exports. Inkscape provides CLI/actions and native SVG. GIMP 3 uses Python plug-ins and GEGL. Adobe apps require their supported UXP/scripting interfaces and licensing; no undocumented automation is assumed. Paint has no professional document API, so semantic UI + verified pointer strokes are the practical path.
- GUI-agent research shows that separate interpretation and grounding, hierarchical plans, verifier loops, and API/GUI hybrids improve reliability. Accessibility/native interfaces should precede screenshots; screenshot-only long horizons remain error-prone.
- Professional production requires brief, references, concepts, blockout, hierarchy/composition, typography/color, construction, cleanup, proofing, preflight, editable source and target-specific exports.

## Engineering recommendations
1. Use typed artifact references rather than placing image bytes in every MCP response.
2. Execute only allowlisted DAG nodes. No arbitrary Python/shell node.
3. Prefer native API → supported plugin → scripting/CLI → accessibility → visual GUI → raw input.
4. Keep physical input in Windows Live Control Agent. Artist emits verified action envelopes and stroke trajectories.
5. Build scene/artwork state independently of any application so conversational edits resolve to stable object IDs.
6. Treat AI generation, SAM, OCR, Blender and vectorizers as lazy optional adapters discovered at runtime.
7. Require explicit approval for installs, application launches, overwrite/export, network model calls and clipboard use.

## Practical vs experimental
**Proven/practical:** Pillow/OpenCV operations; SVG generation; image comparison; local artifact store; FFmpeg/Blender/Inkscape CLI discovery; UIA-first application inspection; Bézier/resampled trajectory generation; layered artwork schema; DAG execution; hardware probing.

**Practical with installation/model:** Tesseract OCR, VTracer, ONNX models, SAM 2, local diffusion/ComfyUI, Blender rendering, Krita plug-in bridge.

**Experimental/unreliable:** zero-shot unknown-application mastery; fully autonomous professional-quality Paint illustration from arbitrary reference; universal scene decomposition; automatic high-quality editable vector reconstruction of photographs; unsupervised long-horizon GUI completion. These require host-side models, an interactive Windows session, calibration and acceptance testing.

## Application interface matrix
- Paint: UIA/vision/input; real strokes; verify canvas changes and save dialog.
- Krita: Python plug-in/libkis first, then actions/UI; strong layers/brushes.
- Photoshop: UXP-supported extension/actions first; UI fallback.
- Illustrator: supported scripting/plugin surfaces; SVG/PDF interchange; UI fallback.
- GIMP 3: Python plug-ins/GEGL/CLI where supported; UI fallback.
- Inkscape: SVG document manipulation plus CLI/actions; excellent vector route.
- Blender: background CLI + bpy scripts with constrained templates; GUI only for interactive gaps.
- ComfyUI: local HTTP/workflow API when installed; generation is a subsystem.
- Unknown app: executable/version discovery → accessibility tree → help/CLI probes → non-destructive tests → capability profile → approval → execution.

## Security
No kernel drivers, hooks, DLL injection, memory reading or privileged services. Subprocesses use executable allowlists, argument arrays, timeout, constrained working directories and captured output. Paths remain inside configured roots. Model/tool installation produces a plan and never runs automatically. External files/screens are untrusted. Destructive actions require approval and verification.

## Acceptance-test reality
This Linux sandbox can test visual algorithms, SVG, trajectory geometry, registry discovery, DAGs, QA and MCP. It cannot truthfully run Windows Paint, UI Automation, Windows capture/input, Photoshop or a GPU not attached to the sandbox. Production acceptance scripts and exact procedures are included; they must run on the authorized Windows workstation.

## Sources
Microsoft High DPI: https://learn.microsoft.com/windows/win32/hidpi/high-dpi-desktop-application-development-on-windows
Windows Graphics Capture: https://learn.microsoft.com/uwp/api/windows.graphics.capture
Krita scripting: https://docs.krita.org/en/user_manual/python_scripting/introduction_to_python_scripting.html
Blender CLI/API: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html and https://docs.blender.org/api/current/
OpenCV: https://docs.opencv.org/
ONNX Runtime: https://onnxruntime.ai/docs/
SAM 2: https://ai.meta.com/blog/segment-anything-2/ and https://arxiv.org/abs/2408.00714
Potrace: https://potrace.sourceforge.net/
VTracer: https://github.com/visioncortex/vtracer
FFmpeg: https://ffmpeg.org/documentation.html
GUI-Actor: https://www.microsoft.com/en-us/research/publication/gui-actor-coordinate-free-visual-grounding-for-gui-agents/
Ponder & Press: https://aclanthology.org/2025.findings-acl.76/
