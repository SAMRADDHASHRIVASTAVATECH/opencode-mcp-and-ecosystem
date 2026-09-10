# Capability map

## A — supplied-code capabilities
| Capability | Input → output | MCP suitability | Limits/risks |
|---|---|---|---|
| Image loading | local common raster → RGB PIL image | High | original lacked EXIF/resource validation |
| Canny/Sobel/Laplacian/Scharr | RGB + blur/thresholds → uint8 edge map | High | method semantics differ; flat normalization bug |
| Hybrid export | raster + edge overlay → EPS/PDF/SVG/PNG | High | backend/format constraints; overwrite risk |
| Batch export | paths + directory → many outputs | High | original hid per-item failure |
| Presets/history/theme | UI state | Presets useful; theme/history not core MCP | user-path privacy and state divergence |

## B — underlying but unused
OpenCV provides thresholding, morphology, contour hierarchy, connected components, area/perimeter descriptors, `findContours`, and Douglas–Peucker `approxPolyDP`. Pillow provides content-based format identification, EXIF transpose, multi-frame/alpha/ICC inspection, controlled decoding and broad format support. Matplotlib offers explicit vector backends, metadata, transparency and rasterization control. MCP provides typed tools, stdio transport and structured JSON results.

These enable true path extraction rather than only `matplotlib.contour`, contour simplification/filtering, quantitative method comparison, robust validation, deterministic headless processing, secure batches, asynchronous status and agent-guided tuning.

## C — implemented agent capabilities
| Capability | Inputs | Outputs | Implementation | Agent value / risk |
|---|---|---|---|---|
| Capability discovery | none | versions, formats, limits | `eps_get_capabilities` | avoids invented support |
| Safe inspection | rooted path | dimensions/format/hash/metadata | Pillow verify + EXIF transpose | detects unsuitable/huge input |
| Edge analysis | path + typed settings | density/components/contours/vertices | OpenCV | guides tuning without writes |
| Method comparison | path + methods | comparable metrics | four detectors | chooses detector rationally |
| True vectorization | edge + vector settings | simplified contour paths | findContours + approxPolyDP | smaller/editable vectors; edge tracing is not semantic object recognition |
| Hybrid SVG | bitmap toggle + paths | explicit SVG paths, optional embedded PNG | native serializer | inspectable/editable output; embedded bitmap increases size |
| EPS/PDF/PNG export | same | backend file | Matplotlib Agg | broad workflows; EPS transparency limitations |
| Exact export planning | input/output/settings | immutable approval plan | digest-bound plan | exposes overwrite/resource impact |
| Async verified execution | approved plan | job/results/hash/size | two-worker pool | long jobs, status, cancellation |
| Bounded batch | ≤1000 files | per-output results | safe rooted paths | useful automation; CPU/memory load |

Not implemented because unsupported by this stack: OCR, semantic scene decomposition, font reconstruction, Bezier fitting beyond polygonal contour simplification, color-region vector tracing comparable to Potrace/Inkscape Trace Bitmap, CMYK/prepress guarantees, or EPS round-trip editing. External Potrace/Inkscape/Ghostscript were not detected.
