"""Lightweight schema/definition loading + validation.

Loads YAML/JSON definition files from this package and validates them against
the bundled JSON Schemas. Kept dependency-light: if `jsonschema` is absent it
falls back to structural checks so tests still run anywhere.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml


def load_yaml(path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def load_json(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_against(instance: dict, schema: dict) -> list[str]:
    """Return list of validation error strings (empty == valid)."""
    errors = []
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        for e in sorted(v.iter_errors(instance), key=lambda x: list(x.path)):
            errors.append(f"{'.'.join(str(p) for p in e.path)}: {e.message}")
        return errors
    except ImportError:
        pass
    # minimal structural fallback: required top-level fields
    required = (schema or {}).get("required", [])
    for req in required:
        if req not in instance:
            errors.append(f"missing required field: {req}")
    return errors


class SchemaValidator:
    def __init__(self, schema_root: str | Path):
        self.schema_root = Path(schema_root)
        self._cache = {}

    def schema(self, name: str) -> dict:
        if name not in self._cache:
            self._cache[name] = load_json(self.schema_root / name)
        return self._cache[name]

    def validate(self, definition: dict, schema_name: str) -> list[str]:
        return validate_against(definition, self.schema(schema_name))

    def validate_files(self, files: list[Path], schema_name: str) -> dict:
        """Validate a set of definition files against one schema."""
        out = {"valid": 0, "invalid": 0, "errors": {}}
        for f in files:
            data = load_yaml(f) if f.suffix in (".yaml", ".yml") else load_json(f)
            errs = self.validate(data, schema_name)
            if errs:
                out["invalid"] += 1
                out["errors"][str(f)] = errs
            else:
                out["valid"] += 1
        return out
