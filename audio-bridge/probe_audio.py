"""Probe Windows audio endpoints (esp. Bluetooth HFP) for openable stream directions.

Empirically determines, for each endpoint:
  - full name / index / hostapi
  - max input & output channels
  - whether an input (capture) stream can be opened
  - whether an output (playback) stream can be opened
  - for output devices that also allow loopback capture (WASAPI), marks loopback-capable

Run:  py probe_audio.py
"""
from __future__ import annotations

import sounddevice as sd


_HOSTAPIS = None


def _hostapi_name(hostapi_idx: int) -> str:
    global _HOSTAPIS
    if _HOSTAPIS is None:
        _HOSTAPIS = {i: h["name"] for i, h in enumerate(sd.query_hostapis())}
    return _HOSTAPIS.get(hostapi_idx, "unknown")


def fmt_dev(d, idx):
    return {
        "index": idx,
        "name": d["name"],
        "hostapi": _hostapi_name(d["hostapi"]),
        "max_in": d["max_input_channels"],
        "max_out": d["max_output_channels"],
        "default_sr": d["default_samplerate"],
    }


def try_open(name, samplerate, channels, kind):
    """kind: 'in' or 'out'. Returns (ok, err)."""
    try:
        sd.Stream(device=name, channels=channels, samplerate=samplerate,
                  dtype="float32").open()
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def probe():
    devices = sd.query_devices()
    print("=== AudioDevice API ===")
    print(f"default in : {sd.default.device[0]}")
    print(f"default out: {sd.default.device[1]}")
    print()

    rows = []
    for idx, d in enumerate(devices):
        rows.append(fmt_dev(d, idx))

    print("=== All devices ===")
    for r in rows:
        print(f"[{r['index']:>2}] {r['name']:<60} in={r['max_in']} out={r['max_out']} sr={r['default_sr']:.0f} {r['hostapi']}")
    print()

    print("=== Direction probe (16kHz, 1ch) ===")
    candidates = []
    for r in rows:
        mark = ""
        in_ok, in_err = False, ""
        out_ok, out_err = False, ""
        if r["max_in"] > 0:
            in_ok, in_err = try_open(r["name"], 16000, 1, "in")
        if r["max_out"] > 0:
            out_ok, out_err = try_open(r["name"], 16000, 1, "out")
        flags = []
        if in_ok:
            flags.append("IN")
        if out_ok:
            flags.append("OUT")

        # WASAPI loopback capture guess: output devices on WASAPI can often be
        # captured with extra_settings loopback; probe it.
        loopback_ok = False
        if out_ok and r["hostapi"].lower().find("wasapi") >= 0:
            try:
                s = sd.Stream(device=(r["name"], r["name"]), channels=(0, 1),
                              samplerate=16000, dtype="float32").open()
                s.close()
                loopback_ok = True
            except Exception as e:
                loopback_ok = False
                out_err_loop = f"{type(e).__name__}: {e}"
            if loopback_ok:
                flags.append("LOOPBACK")
        if flags:
            candidates.append((r, flags, in_err, out_err, loopback_ok))
            mark = " <-- " + "+".join(flags)
        if in_err:
            mark += f"  [in:{in_err[:60]}]"
        if out_err and not out_ok:
            mark += f"  [out:{out_err[:60]}]"
        print(f"[{r['index']:>2}] {r['name']:<60}{mark}")
    print()

    print("=== Summary of usable directions ===")
    for r, flags, _, _, _ in candidates:
        print(f"  IN  : {r['name']}  -> {'+'.join(flags)}")
    print()


if __name__ == "__main__":
    probe()