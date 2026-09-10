#!/usr/bin/env python3
"""Thin launcher so the skill runs from anywhere without pip install:
    python scripts/image_to_3d.py <image> [options]
    python scripts/image_to_3d.py --detect
    python scripts/image_to_3d.py --dry-run <image>
Adds this scripts/ dir to sys.path, then invokes the i3dc CLI.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from i3dc.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
