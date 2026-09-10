# Windows acceptance protocol
Requires an interactive authorized Windows user session and a configured Windows Live Control Agent. Run as a standard user.

## Preconditions
1. Enable Per-Monitor V2 awareness in the Live Agent; record monitor DPI, window bounds, client bounds, canvas bounds, zoom and scroll.
2. Confirm emergency stop independently releases pointer/keys and revokes control.
3. Deny elevation, secure desktop, credential fields and other integrity levels.
4. Record Paint version, Windows version, display topology and test artifact hashes.

## Genuine Paint test
1. Artist creates a project and workflow from a reference brief.
2. Live Agent launches Paint after approval; inspect UIA tree and capture canvas changed regions.
3. Calibrate canvas-to-physical-pixel transform using non-destructive pointer landmarks; verify against observed cursor/canvas.
4. Artist creates several trajectories for outline, large fills and details. Live Agent verifies foreground and bounds before every dispatch.
5. Dispatch actual user-mode pointer down/move/up samples. Do **not** paste/import a generated bitmap.
6. After each stroke group, observe changed ROI, compare expected occupancy/silhouette/color, and request targeted corrective strokes when outside tolerance.
7. Save through Paint UI to a new PNG after approval. Verify file exists, decodes, dimensions match and its pixels correspond to observed canvas.
8. Exercise emergency stop mid-stroke and confirm release within Live Agent SLA.
9. Move Paint across mixed-DPI monitors, recalibrate, draw a bounded stroke, and verify no offset.

A pass requires audit records for pointer dispatch, observations, corrections and save. The Linux development validation cannot count as this pass.

## Other host tests
- UIA application discovery and unknown-app non-destructive probe.
- Windows Graphics Capture changed-region path with minimized/occluded states handled.
- DirectML provider probe and CPU fallback.
- Krita/Inkscape/Blender native adapter smoke tests if installed.
- Multi-monitor, scaling, window movement, canvas zoom/scroll and focus loss.
