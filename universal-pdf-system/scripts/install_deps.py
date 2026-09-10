#!/usr/bin/env python3
"""Install the core + optional dependencies for the Universal PDF System.

Usage:
    python scripts/install_deps.py            # core only
    python scripts/install_deps.py --all      # + optional openpyxl, docx, pytest
"""
import subprocess
import sys

CORE = ["pymupdf", "reportlab", "pypdf", "pdfplumber", "pillow"]
OPT = ["openpyxl", "python-docx", "pytest"]


def run(pkgs):
    if not pkgs:
        return
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + pkgs)


def main():
    run(CORE)
    if "--all" in sys.argv:
        run(OPT)
    print("Installed:", ", ".join(CORE + (OPT if "--all" in sys.argv else [])))


if __name__ == "__main__":
    main()
