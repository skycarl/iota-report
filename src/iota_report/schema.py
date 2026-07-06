"""Canonical JSON Schema export for the portable occultation report.

``SCHEMA_VERSION`` is the semantic version of the *schema* (the wire contract),
distinct from the package version in ``pyproject.toml``. It is the default of
``Report.schema_version`` and is embedded in the schema ``$id``.

This module deliberately performs no top-level import of ``models`` so that
``models`` can import ``SCHEMA_VERSION`` from here without a circular import;
``export_schema`` imports ``Report`` lazily.
"""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "1.0.0"

_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


def schema_id(version: str = SCHEMA_VERSION) -> str:
    """The canonical, version-pinned ``$id`` for the schema."""
    return (
        "https://raw.githubusercontent.com/skycarl/iota-report/"
        f"v{version}/schema/iota-report.schema.json"
    )


def export_schema() -> dict[str, Any]:
    """Return the canonical draft-2020-12 JSON Schema for :class:`Report`.

    Stamps ``$schema`` and a version-pinned ``$id``. The result is deterministic
    for a given package version, so ``scripts/export_schema.py`` can serialize it
    with ``sort_keys=True`` for stable diffs and a CI drift check.
    """
    from iota_report.models import Report

    schema = Report.model_json_schema()
    stamped = {
        "$schema": _SCHEMA_DIALECT,
        "$id": schema_id(),
        **schema,
    }
    return stamped
