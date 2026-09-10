"""Language boilerplate used by the ASCII-tree creator and se_ascii_create."""

from __future__ import annotations

import os

LANG_TEMPLATES = {
    ".py": {
        "import": lambda mods: "\n".join(f"import {m.replace('/', '.')}" for m in mods),
        "main": lambda name, calls: (
            "def main():\n"
            "    print('PLACEHOLDER: {}'){}\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        ).format(
            name,
            "".join(
                f"\n    {os.path.splitext(m.replace(chr(92), '/'))[0].replace('/', '.')}.main()"
                for m in calls
            ),
        ),
    },
    ".js": {
        "import": lambda mods: "\n".join(f"const {m.split('/')[-1]} = require('./{m}');" for m in mods),
        "main": lambda name, calls: (
            "function main() {{\n"
            "    console.log('PLACEHOLDER: {}');{}\n"
            "}}\n\nmain();\n"
        ).format(name, "".join(f"\n    {m.split('/')[-1]}.main();" for m in calls)),
    },
    ".ts": {
        "import": lambda mods: "\n".join(
            f"import {{ main as {m.split('/')[-1]}Main }} from './{m}';" for m in mods
        ),
        "main": lambda name, calls: (
            "function main(): void {{\n"
            "    console.log('PLACEHOLDER: {file}');{calls}\n}}\n\nmain();"
        ).format(
            file=name,
            calls="".join(f"\n    {os.path.splitext(m.split('/')[-1])[0]}Main();" for m in calls),
        ),
    },
    ".java": {
        "import": lambda mods: "\n".join(f"import {m.replace('/', '.')};" for m in mods),
        "main": lambda name, calls: (
            "public class {cls} {{\n"
            "    public static void main(String[] args) {{\n"
            "        System.out.println(\"PLACEHOLDER: {cls}\");{calls}\n"
            "    }}\n"
            "}}\n"
        ).format(
            cls=os.path.splitext(os.path.basename(name))[0].capitalize(),
            calls="".join(
                f"\n        {os.path.splitext(os.path.basename(m))[0].capitalize()}.main(args);"
                for m in calls
            ),
        ),
    },
    ".c": {
        "import": lambda mods: "\n".join(f'#include "{os.path.basename(m)}.h"' for m in mods),
        "main": lambda name, calls: (
            "#include <stdio.h>\n"
            "int main() {\n"
            '    printf("PLACEHOLDER: %s\\n", "{file}");{calls}\n'
            "    return 0;\n"
            "}\n"
        ).format(
            file=name,
            calls="".join(f"\n    {os.path.splitext(os.path.basename(m))[0]}_main();" for m in calls),
        ),
    },
    ".cpp": {
        "import": lambda mods: "\n".join(f'#include "{os.path.basename(m)}.h"' for m in mods),
        "main": lambda name, calls: (
            "#include <iostream>\n"
            "int main() {{\n"
            '    std::cout << "PLACEHOLDER: {file}" << std::endl;{calls}\n'
            "    return 0;\n"
            "}}\n"
        ).format(
            file=name,
            calls="".join(f"\n    {os.path.splitext(os.path.basename(m))[0]}_main();" for m in calls),
        ),
    },
    ".go": {
        "import": lambda mods: ("import (\n" + "\n".join(f'\t"{m}"' for m in mods) + "\n)" if mods else ""),
        "main": lambda name, calls: (
            "package main\n\nimport \"fmt\"\n\nfunc main() {{\n"
            '    fmt.Println("PLACEHOLDER: {file}"){calls}\n}}\n'
        ).format(
            file=name,
            calls="".join(
                f"\n    {os.path.splitext(os.path.basename(m))[0]}.Main()" for m in calls
            ),
        ),
    },
    ".rs": {
        "import": lambda mods: "\n".join(
            f"// use crate::{os.path.splitext(os.path.basename(m))[0]};" for m in mods
        ),
        "main": lambda name, calls: (
            "fn main() {{\n"
            '    println!("PLACEHOLDER: {file}");{calls}\n}}'
        ).format(
            file=name,
            calls="".join(
                f"\n    // {os.path.splitext(os.path.basename(m))[0]}::main();" for m in calls
            ),
        ),
    },
    ".php": {
        "import": lambda mods: "\n".join(f'require_once("{m}.php");' for m in mods),
        "main": lambda name, calls: (
            "<?php\nfunction main() {{\n"
            '    echo "PLACEHOLDER: {file}\\n";{calls}\n'
            "}}\nmain();\n?>"
        ).format(
            file=name,
            calls="".join(f"\n    {os.path.splitext(os.path.basename(m))[0]}_main();" for m in calls),
        ),
    },
    ".rb": {
        "import": lambda mods: "\n".join(f"require_relative '{m}'" for m in mods),
        "main": lambda name, calls: (
            "def main\n"
            "  puts 'PLACEHOLDER: {file}'{calls}\nend\n\nmain\n"
        ).format(
            file=name,
            calls="".join(f"\n  {os.path.splitext(os.path.basename(m))[0]}_main()" for m in calls),
        ),
    },
    ".sh": {
        "import": lambda mods: "\n".join(f". ./{m}.sh" for m in mods),
        "main": lambda name, calls: (
            "#!/bin/bash\nmain() {{\n"
            "    echo 'PLACEHOLDER: {file}'{calls}\n}}\n\nmain \"$@\"\n"
        ).format(
            file=name,
            calls="".join(f"\n    {os.path.splitext(os.path.basename(m))[0]}_main" for m in calls),
        ),
    },
}

LANG_EXTS = set(LANG_TEMPLATES.keys())
ASSET_PLACEHOLDER = "# PLACEHOLDER ASSET FILE: {ext}"
GENERIC_PLACEHOLDER = "# PLACEHOLDER: {kind} ({name})"
ASSET_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".bmp",
    ".webp",
    ".tiff",
    ".mp3",
    ".wav",
    ".ogg",
    ".mp4",
    ".avi",
    ".mkv",
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".zip",
    ".tar",
    ".gz",
    ".dll",
    ".exe",
    ".bin",
}


def detect_lang(path: str) -> str | None:
    ext = os.path.splitext(path)[1].lower()
    return ext if ext in LANG_EXTS else None


def get_all_code_files(tree_paths: list[tuple[str, str]]) -> list[str]:
    return [p for p, typ in tree_paths if typ == "file" and detect_lang(p)]


def format_module_path(m_path: str, current_ext: str) -> str:
    m_path_rel = m_path.replace("\\", "/")
    base_name, _ = os.path.splitext(m_path_rel)
    if current_ext in {".js", ".ts"}:
        return base_name
    if current_ext == ".py":
        return base_name.replace("/", ".")
    if current_ext == ".go":
        return os.path.dirname(m_path_rel) or "."
    return base_name


def build_interconnected_boilerplate(path: str, ext: str, codefiles: list[str]) -> str:
    rel_this = path.replace("\\", "/")
    mods, calls = [], []
    for m in codefiles:
        relm = m.replace("\\", "/")
        if relm != rel_this:
            formatted = format_module_path(m, ext)
            mods.append(formatted)
            calls.append(m)
    tpl = LANG_TEMPLATES.get(ext, {})
    imp = tpl["import"](mods) if tpl.get("import") else ""
    main = tpl["main"](os.path.basename(path), calls) if tpl.get("main") else ""
    if not (imp or main):
        return GENERIC_PLACEHOLDER.format(kind=f"{ext} Code File", name=os.path.basename(path))
    return (imp + "\n\n" + main).strip()


def placeholder_for(path: str, inject: bool, codefiles: list[str]) -> str:
    if not inject:
        return ""
    ext = detect_lang(path)
    if ext:
        return build_interconnected_boilerplate(path, ext, codefiles)
    ext_lower = os.path.splitext(path)[1].lower()
    if ext_lower in ASSET_EXTS:
        return ASSET_PLACEHOLDER.format(ext=ext_lower[1:].upper())
    return GENERIC_PLACEHOLDER.format(kind="Asset/Text/Unknown", name=os.path.basename(path))
