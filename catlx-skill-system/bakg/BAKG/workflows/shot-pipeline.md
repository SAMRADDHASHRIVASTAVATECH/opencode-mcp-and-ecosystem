# Workflow: Shot Pipeline (image chain)

```
beat (D01) → shot design (D106) → board (D09) → animatic (D10) → previs (D11)
→ layout / camera (D102) → animation (D64) → secondary/sim (D77/D88)
→ lighting (D108) → VFX (D100) → render with passes (D112/D115)
→ comp (D117) → color (D118/D119) → edit (D120) → QC (D127)
```

Shot status ladder: planned → blocked → splined → animated → sim'd → lit → rendered → comped → approved.

Render in dependency order. EXR per frame (crash-safe). Re-render only failed frames.
