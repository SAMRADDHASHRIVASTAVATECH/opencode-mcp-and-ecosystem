# Technology research
OpenCV 4.13 documentation confirms Canny, Sobel, Scharr (more accurate than 3×3 Sobel), Laplacian, contour retrieval modes and `approxPolyDP` Douglas–Peucker simplification. `findContours` treats nonzero binary pixels as foreground and can preserve external/list/two-level/tree hierarchy.

Pillow documentation confirms broad content-identified raster reading, `ImageOps.exif_transpose`, frame/format-specific behavior, and decompression protections. This implementation verifies then decodes, transposes orientation, limits to 80 MP, and records alpha/ICC/EXIF presence without copying private metadata into exports.

Matplotlib `savefig` supports backend-dependent PNG/PDF/SVG/EPS and metadata; vector outputs can contain rasterized artists. Here SVG is serialized directly into explicit polygonal paths plus optional embedded PNG. EPS/PDF/PNG use the noninteractive Agg workflow.

The official MCP Python SDK supports tool schemas and stdio. A local stdio server is appropriate because processing local files does not need network exposure or authentication; the root path and exact write approval are its security boundaries.
