"""Write the canonical JSON Schema to schema/iota-report.schema.json.

Run with:  uv run python scripts/export_schema.py

Serialized with sorted keys and a trailing newline so the committed file is
byte-stable, enabling a CI drift check (regenerate + ``git diff --exit-code``).
"""

from __future__ import annotations

import json
from pathlib import Path

from iota_report.schema import export_schema

SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent / "schema" / "iota-report.schema.json"
)


def main() -> None:
    schema = export_schema()
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_PATH.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote {SCHEMA_PATH}")


if __name__ == "__main__":
    main()
