# Examples

Runnable demonstrations. `demo.py` exercises the whole system (create →
inspect → search → tables → merge/watermark/compress → SYSTEM MODE → convert)
and cleans up after itself unless you pass `--keep`.

```bash
python examples/demo.py          # prints results, auto-cleans temp outputs
python examples/demo.py --keep   # keeps outputs under examples/output/
```

Inputs used by the demo:
- `../templates/report-template.json` — JSON content → `pdf-create`
- `../templates/invoice-template.json`
- `../templates/content/sample.md` — Markdown → `pdf-create`

For deeper per-skill usage, see `docs/USAGE.md` and the `tests/` suite.
