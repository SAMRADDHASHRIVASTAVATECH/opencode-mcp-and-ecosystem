"""Multi-stack project templates. Not MERN-only."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from se_mcp.env import detect
from se_mcp.errors import ValidationError

TEMPLATES = (
    "python-cli",
    "python-lib",
    "python-fastapi",
    "python-flask",
    "python-desktop",
    "node-cli",
    "node-express",
    "node-library",
    "static-web",
    "java-cli",
    "c-cli",
    "go-cli",
    "rust-cli",
)


def slug(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    if not s:
        raise ValidationError("Invalid name")
    return s


def ident(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip()).strip("_")
    if not s or s[0].isdigit():
        raise ValidationError("Invalid identifier")
    return s


def _w(root: Path, rel: str, content: str, files: list[str]) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    p.write_text(content.lstrip("\n") if content.startswith("\n") else content, encoding="utf-8")
    files.append(rel)


def create_project(dest: Path, *, name: str, template: str, overwrite: bool = False) -> dict[str, Any]:
    template = template.lower().replace("_", "-")
    if template not in TEMPLATES:
        raise ValidationError(f"template must be one of {TEMPLATES}")
    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.iterdir()) and not overwrite:
        raise ValidationError("Destination not empty; pass overwrite=true")
    files: list[str] = []
    sl = slug(name)
    fn = globals()[f"_t_{template.replace('-', '_')}"]
    fn(dest, name, sl, files)
    env = detect()
    return {
        "path": str(dest),
        "template": template,
        "files": files,
        "file_count": len(files),
        "host": {
            "can_python": env["can_python"],
            "can_node": env["can_node"],
            "can_java": env["can_java"],
            "can_c": env["can_c"],
            "can_go": env["can_go"],
            "can_rust": env["can_rust"],
        },
        "next": ["se_discover_project", "se_test", "se_build"],
        "not_for": "Android apps → android_create_project; Office files → office_create; SQL → db_connect",
    }


def _t_python_cli(root, name, sl, files):
    pkg = ident(sl.replace("-", "_"))
    _w(root, "pyproject.toml", f'''
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
[project]
name = "{sl}"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = []
[project.optional-dependencies]
dev = ["pytest>=7"]
[project.scripts]
{sl} = "{pkg}.cli:main"
[tool.setuptools.packages.find]
where = ["src"]
[tool.pytest.ini_options]
pythonpath = ["src"]
''', files)
    _w(root, f"src/{pkg}/__init__.py", '__version__ = "0.1.0"\n', files)
    _w(root, f"src/{pkg}/cli.py", f'''
from __future__ import annotations
import argparse
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="{sl}", description="{name}")
    p.add_argument("name", nargs="?", default="world")
    args = p.parse_args(argv)
    print(f"hello, {{args.name}}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
''', files)
    _w(root, f"tests/test_cli.py", f'''
from {pkg}.cli import main
def test_hello():
    assert main(["Ada"]) == 0
''', files)
    _w(root, "README.md", f"# {name}\n\nPython CLI. `{sl} [name]`\n", files)
    _w(root, ".gitignore", ".venv/\n__pycache__/\ndist/\n", files)


def _t_python_lib(root, name, sl, files):
    pkg = ident(sl.replace("-", "_"))
    _w(root, "pyproject.toml", f'''
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
[project]
name = "{sl}"
version = "0.1.0"
requires-python = ">=3.10"
[tool.setuptools.packages.find]
where = ["src"]
''', files)
    _w(root, f"src/{pkg}/__init__.py", f'''
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b
''', files)
    _w(root, f"tests/test_add.py", f"from {pkg} import add\ndef test_add():\n    assert add(2, 3) == 5\n", files)
    _w(root, "README.md", f"# {name}\n\nPython library.\n", files)


def _t_python_fastapi(root, name, sl, files):
    pkg = ident(sl.replace("-", "_"))
    _w(root, "pyproject.toml", f'''
[project]
name = "{sl}"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["fastapi>=0.110", "uvicorn[standard]>=0.27"]
[project.optional-dependencies]
dev = ["pytest>=7", "httpx>=0.27"]
''', files)
    _w(root, f"src/{pkg}/app.py", '''
from fastapi import FastAPI
app = FastAPI()
@app.get("/health")
def health():
    return {"ok": True}
''', files)
    _w(root, f"tests/test_health.py", f'''
from fastapi.testclient import TestClient
from {pkg}.app import app
def test_health():
    c = TestClient(app)
    assert c.get("/health").json()["ok"] is True
''', files)
    _w(root, "README.md", f"# {name}\n\nuvicorn {pkg}.app:app --reload\n", files)


def _t_python_flask(root, name, sl, files):
    pkg = ident(sl.replace("-", "_"))
    _w(root, "pyproject.toml", f'''
[project]
name = "{sl}"
version = "0.1.0"
dependencies = ["flask>=3.0"]
''', files)
    _w(root, f"src/{pkg}/app.py", '''
from flask import Flask, jsonify
def create_app():
    app = Flask(__name__)
    @app.get("/health")
    def health():
        return jsonify(ok=True)
    return app
app = create_app()
''', files)
    _w(root, "README.md", f"# {name}\n\nflask --app {pkg}.app run\n", files)


def _t_python_desktop(root, name, sl, files):
    pkg = ident(sl.replace("-", "_"))
    _w(root, "pyproject.toml", f"[project]\nname = \"{sl}\"\nversion = \"0.1.0\"\nrequires-python = \">=3.10\"\n", files)
    _w(root, f"src/{pkg}/main.py", f'''
import tkinter as tk
def main():
    root = tk.Tk()
    root.title("{name}")
    tk.Label(root, text="Hello {name}", padx=24, pady=24).pack()
    root.mainloop()
if __name__ == "__main__":
    main()
''', files)
    _w(root, "README.md", f"# {name}\n\nTkinter desktop app (stdlib). For native Win32 admin use windows-system-mcp, not this GUI.\n", files)


def _t_node_cli(root, name, sl, files):
    pkg = {
        "name": sl,
        "version": "0.1.0",
        "bin": {sl: "./bin/cli.js"},
        "type": "module",
        "scripts": {"test": "node --test"},
    }
    _w(root, "package.json", json.dumps(pkg, indent=2), files)
    _w(root, "bin/cli.js", f'''#!/usr/bin/env node
const name = process.argv[2] || "world";
console.log(`hello, ${{name}}`);
''', files)
    _w(root, "test/cli.test.js", '''
import { test } from "node:test";
import assert from "node:assert/strict";
test("placeholder", () => assert.equal(1 + 1, 2));
''', files)
    _w(root, "README.md", f"# {name}\n\nnode bin/cli.js\n", files)


def _t_node_express(root, name, sl, files):
    pkg = {
        "name": sl,
        "version": "0.1.0",
        "type": "module",
        "scripts": {"start": "node src/server.js", "test": "node --test"},
        "dependencies": {"express": "^4.21.0"},
    }
    _w(root, "package.json", json.dumps(pkg, indent=2), files)
    _w(root, "src/server.js", '''
import express from "express";
export function createApp() {
  const app = express();
  app.get("/health", (_req, res) => res.json({ ok: true }));
  return app;
}
if (import.meta.url === `file://${process.argv[1]}`) {
  createApp().listen(process.env.PORT || 3000);
}
''', files)
    _w(root, "README.md", f"# {name}\n\nnpm install && npm start\n", files)


def _t_node_library(root, name, sl, files):
    _w(root, "package.json", json.dumps({"name": sl, "version": "0.1.0", "type": "module", "main": "src/index.js", "scripts": {"test": "node --test"}}, indent=2), files)
    _w(root, "src/index.js", "export function add(a, b) { return a + b; }\n", files)
    _w(root, "test/add.test.js", 'import { test } from "node:test";\nimport assert from "node:assert/strict";\nimport { add } from "../src/index.js";\ntest("add", () => assert.equal(add(2,3), 5));\n', files)
    _w(root, "README.md", f"# {name}\n", files)


def _t_static_web(root, name, sl, files):
    _w(root, "index.html", f'''<!doctype html>
<html lang="en">
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{name}</title>
<link rel="stylesheet" href="styles.css"/>
<h1>{name}</h1>
<p>Static site. No framework required.</p>
<script src="app.js"></script>
</html>
''', files)
    _w(root, "styles.css", "body{font-family:system-ui;margin:2rem;color:#111}\n", files)
    _w(root, "app.js", "console.log('ready');\n", files)
    _w(root, "README.md", f"# {name}\n\nOpen index.html or any static file server.\n", files)


def _t_java_cli(root, name, sl, files):
    cls = ident(name.replace("-", "_")).title().replace("_", "")
    _w(root, f"src/{cls}.java", f'''
public class {cls} {{
    public static void main(String[] args) {{
        String n = args.length > 0 ? args[0] : "world";
        System.out.println("hello, " + n);
    }}
}}
''', files)
    _w(root, "Makefile", f"all:\n\tjavac -d out src/{cls}.java\nrun: all\n\tjava -cp out {cls}\n", files)
    _w(root, "README.md", f"# {name}\n\nmake run\n", files)


def _t_c_cli(root, name, sl, files):
    _w(root, "src/main.c", '''
#include <stdio.h>
int main(int argc, char **argv) {
    const char *n = argc > 1 ? argv[1] : "world";
    printf("hello, %s\\n", n);
    return 0;
}
''', files)
    _w(root, "Makefile", "CC=gcc\nall: bin/app\nbin/app: src/main.c\n\tmkdir -p bin && $(CC) -Wall -o bin/app src/main.c\nrun: all\n\t./bin/app\ntest: all\n\t./bin/app test >/dev/null\n", files)
    _w(root, "README.md", f"# {name}\n\nmake run\n", files)


def _t_go_cli(root, name, sl, files):
    _w(root, "go.mod", f"module {sl}\n\ngo 1.22\n", files)
    _w(root, "main.go", '''
package main
import ("fmt"; "os")
func main() {
    n := "world"
    if len(os.Args) > 1 { n = os.Args[1] }
    fmt.Println("hello,", n)
}
''', files)
    _w(root, "README.md", f"# {name}\n\ngo run .\nRequires Go toolchain (se_detect_environment).\n", files)


def _t_rust_cli(root, name, sl, files):
    _w(root, "Cargo.toml", f'[package]\nname = "{sl}"\nversion = "0.1.0"\nedition = "2021"\n', files)
    _w(root, "src/main.rs", '''
fn main() {
    let n = std::env::args().nth(1).unwrap_or_else(|| "world".into());
    println!("hello, {n}");
}
''', files)
    _w(root, "README.md", f"# {name}\n\ncargo run\nRequires Rust (cargo).\n", files)
