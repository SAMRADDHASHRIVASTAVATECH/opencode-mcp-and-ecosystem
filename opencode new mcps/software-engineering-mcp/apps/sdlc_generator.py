#!/usr/bin/env python3
"""Universal SDLC Generator — GUI over se_mcp.sdlc."""

from __future__ import annotations

import sys
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import tkinter as tk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from se_mcp.sdlc import (  # noqa: E402
    blended_complexity,
    export_structure,
    generate_blueprint,
)
from se_mcp.sdlc_data import PROJECT_AUDIENCES, PROJECT_CATEGORIES, SDLC_PHASES  # noqa: E402

LIGHT = {"bg": "#eef2ff", "fg": "#111827", "entry": "#ffffff"}
DARK = {"bg": "#0f172a", "fg": "#e2e8f0", "entry": "#1e293b"}


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Universal SDLC Generator")
        self.geometry("1040x700")
        self.dark = False
        self._build()
        self._theme()
        self.refresh_types()
        self.preview()

    def _build(self) -> None:
        form = ttk.Frame(self, padding=8)
        form.pack(fill="x")

        self.name = tk.StringVar(value="MyProject")
        self.audience = tk.StringVar(value=next(iter(PROJECT_AUDIENCES)))
        self.category = tk.StringVar(value=next(iter(PROJECT_CATEGORIES)))
        self.ptype = tk.StringVar()
        self.complexity = tk.StringVar(value="MEDIUM")

        ttk.Label(form, text="Project").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.name, width=28).grid(row=0, column=1, padx=4)
        ttk.Label(form, text="Audience").grid(row=0, column=2, sticky="w")
        aud = ttk.Combobox(form, textvariable=self.audience, values=list(PROJECT_AUDIENCES), width=28, state="readonly")
        aud.grid(row=0, column=3, padx=4)
        aud.bind("<<ComboboxSelected>>", lambda _e: self.preview())

        ttk.Label(form, text="Category").grid(row=1, column=0, sticky="w")
        cat = ttk.Combobox(form, textvariable=self.category, values=list(PROJECT_CATEGORIES), width=28, state="readonly")
        cat.grid(row=1, column=1, padx=4, pady=4)
        cat.bind("<<ComboboxSelected>>", lambda _e: self.refresh_types())

        ttk.Label(form, text="Type").grid(row=1, column=2, sticky="w")
        self.type_box = ttk.Combobox(form, textvariable=self.ptype, width=28, state="readonly")
        self.type_box.grid(row=1, column=3, padx=4, pady=4)
        self.type_box.bind("<<ComboboxSelected>>", lambda _e: self.preview())

        ttk.Label(form, text="Complexity").grid(row=2, column=0, sticky="w")
        cpx = ttk.Combobox(form, textvariable=self.complexity, values=["AUTO", "LOW", "MEDIUM", "HIGH"], width=12, state="readonly")
        cpx.grid(row=2, column=1, sticky="w", padx=4)
        cpx.bind("<<ComboboxSelected>>", lambda _e: self.preview())

        ttk.Button(form, text="Generate preview", command=self.preview).grid(row=2, column=2, padx=4)
        ttk.Button(form, text="Export to disk…", command=self.export).grid(row=2, column=3, sticky="w", padx=4)
        ttk.Button(form, text="Toggle theme", command=self.toggle).grid(row=0, column=4, padx=8)

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=8, pady=8)
        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=3)
        paned.add(right, weight=2)
        ttk.Label(left, text="Structure / ASCII tree").pack(anchor="w")
        self.tree = tk.Text(left, wrap="none", font=("Consolas", 10))
        self.tree.pack(fill="both", expand=True)
        ttk.Label(right, text="21 SDLC phases (depth for this complexity)").pack(anchor="w")
        self.phases = tk.Text(right, wrap="word", font=("Consolas", 10))
        self.phases.pack(fill="both", expand=True)

    def _theme(self) -> None:
        pal = DARK if self.dark else LIGHT
        self.configure(bg=pal["bg"])
        for w in (self.tree, self.phases):
            w.configure(bg=pal["entry"], fg=pal["fg"], insertbackground=pal["fg"])

    def toggle(self) -> None:
        self.dark = not self.dark
        self._theme()

    def refresh_types(self) -> None:
        items = PROJECT_CATEGORIES.get(self.category.get(), {}).get("items", [])
        self.type_box["values"] = items
        if items:
            self.ptype.set(items[0])
        self.preview()

    def _complexity(self) -> str | None:
        v = self.complexity.get()
        if v == "AUTO":
            return None
        return v

    def preview(self) -> None:
        try:
            bp = generate_blueprint(
                self.name.get() or "Project",
                self.audience.get(),
                self.category.get(),
                self.ptype.get() or "Generic",
                self._complexity(),
            )
        except Exception as exc:
            self.tree.delete("1.0", "end")
            self.tree.insert("1.0", str(exc))
            return
        self.tree.delete("1.0", "end")
        header = (
            f"{bp['project_name']}  |  {bp['audience']}  |  {bp['category']} / {bp['type']}\n"
            f"Complexity: {bp['complexity']}   Route: {bp['route_hint']}\n\n"
        )
        self.tree.insert("1.0", header + bp["ascii_tree"])
        self.phases.delete("1.0", "end")
        self.phases.insert("1.0", "\n".join(bp["phases"]))
        _ = blended_complexity  # referenced for GUI parity with catalog
        _ = SDLC_PHASES

    def export(self) -> None:
        dest = filedialog.askdirectory(title="Export structure under…")
        if not dest:
            return
        if not messagebox.askyesno("Confirm", f"Write SDLC folders/files under\n{dest}?"):
            return
        try:
            bp = generate_blueprint(
                self.name.get() or "Project",
                self.audience.get(),
                self.category.get(),
                self.ptype.get() or "Generic",
                self._complexity(),
            )
            written = export_structure(Path(dest), bp["structure"])
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))
            return
        messagebox.showinfo("Exported", f"Dirs {written['dirs']}, files {written['files']}\n{written['base']}")


if __name__ == "__main__":
    App().mainloop()
