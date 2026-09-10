#!/usr/bin/env python3
"""ASCII Tree File System Creator — GUI over se_mcp.ascii_tree."""

from __future__ import annotations

import sys
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import tkinter as tk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from se_mcp.ascii_tree import create_from_tree, folder_to_ascii_tree, parse_ascii_tree  # noqa: E402

SAMPLE = """my_project/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── README.md
"""

LIGHT = {"bg": "#f4f1ea", "fg": "#1f2933", "accent": "#0f766e", "entry": "#fffef9"}
DARK = {"bg": "#1a1f2b", "fg": "#e8eef7", "accent": "#2dd4bf", "entry": "#111827"}


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ASCII Tree File System Creator")
        self.geometry("980x640")
        self.dark = False
        self._build()
        self._theme()

    def _build(self) -> None:
        bar = ttk.Frame(self, padding=8)
        bar.pack(fill="x")
        ttk.Button(bar, text="Scan folder…", command=self.scan).pack(side="left", padx=4)
        ttk.Button(bar, text="Create on disk…", command=self.create).pack(side="left", padx=4)
        ttk.Button(bar, text="Validate parse", command=self.validate).pack(side="left", padx=4)
        ttk.Button(bar, text="Toggle theme", command=self.toggle).pack(side="right", padx=4)

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=8, pady=8)
        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=3)
        paned.add(right, weight=2)

        ttk.Label(left, text="ASCII tree").pack(anchor="w")
        self.tree = tk.Text(left, wrap="none", undo=True, font=("Consolas", 11))
        self.tree.pack(fill="both", expand=True)
        self.tree.insert("1.0", SAMPLE)

        ttk.Label(right, text="Parse result").pack(anchor="w")
        self.out = tk.Text(right, wrap="none", font=("Consolas", 10), state="disabled")
        self.out.pack(fill="both", expand=True)

    def _theme(self) -> None:
        pal = DARK if self.dark else LIGHT
        self.configure(bg=pal["bg"])
        for w in (self.tree, self.out):
            w.configure(bg=pal["entry"], fg=pal["fg"], insertbackground=pal["fg"])

    def toggle(self) -> None:
        self.dark = not self.dark
        self._theme()

    def _set_out(self, text: str) -> None:
        self.out.configure(state="normal")
        self.out.delete("1.0", "end")
        self.out.insert("1.0", text)
        self.out.configure(state="disabled")

    def scan(self) -> None:
        folder = filedialog.askdirectory(title="Folder to scan")
        if not folder:
            return
        try:
            rendered = folder_to_ascii_tree(folder)
            self.tree.delete("1.0", "end")
            self.tree.insert("1.0", rendered)
            self._set_out(f"Scanned {folder}\n{len(rendered.splitlines())} lines")
        except Exception as exc:
            messagebox.showerror("Scan failed", str(exc))

    def validate(self) -> None:
        try:
            parsed = parse_ascii_tree(self.tree.get("1.0", "end"))
        except Exception as exc:
            messagebox.showerror("Parse failed", str(exc))
            return
        lines = [f"{kind:4}  {path}" for path, kind in parsed]
        self._set_out("\n".join(lines) or "(empty)")

    def create(self) -> None:
        dest = filedialog.askdirectory(title="Create structure under…")
        if not dest:
            return
        if not messagebox.askyesno("Confirm", f"Write folders/files under\n{dest}?"):
            return
        try:
            result = create_from_tree(self.tree.get("1.0", "end"), Path(dest), inject_boilerplate=True)
        except Exception as exc:
            messagebox.showerror("Create failed", str(exc))
            return
        self._set_out(
            f"Folders: {result['folders_created']}\n"
            f"Files: {result['files_created']}\n"
            f"Skipped: {result['skipped_existing']}\n"
            f"Errors: {result['errors'] or 'none'}"
        )
        messagebox.showinfo("Done", f"Created under {dest}")


if __name__ == "__main__":
    App().mainloop()
