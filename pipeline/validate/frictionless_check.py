"""Frictionless-level validation: types, enums, patterns, required fields, primary keys.

Resources are validated one by one from the repo root (frictionless treats the
descriptor's ``../data/...`` paths as unsafe when loaded as a Package, so we
resolve paths ourselves).
"""

from __future__ import annotations

import json
from pathlib import Path

from frictionless import Resource, Schema, system

from pipeline import DATAPACKAGE


def iter_resources(datapackage_path: Path = DATAPACKAGE):
    descriptor = json.loads(datapackage_path.read_text(encoding="utf-8"))
    base = datapackage_path.parent
    for res in descriptor["resources"]:
        yield res["name"], (base / res["path"]).resolve(), res["schema"]


def validate_resources(datapackage_path: Path = DATAPACKAGE) -> list[str]:
    """Return a list of human-readable error strings (empty = valid)."""
    errors: list[str] = []
    for name, csv_path, schema_descriptor in iter_resources(datapackage_path):
        if not csv_path.exists():
            errors.append(f"{name}: missing file {csv_path}")
            continue
        # Foreign keys are enforced in cross_table.py with pandas joins;
        # strip them here so single-resource validation doesn't fail on lookups.
        schema_descriptor = {k: v for k, v in schema_descriptor.items() if k != "foreignKeys"}
        with system.use_context(trusted=True):
            resource = Resource(path=str(csv_path), schema=Schema.from_descriptor(schema_descriptor))
            report = resource.validate()
        if not report.valid:
            for task in report.tasks:
                for err in task.errors:
                    errors.append(f"{name}: {err.title}: {err.message}")
    return errors
