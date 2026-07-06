"""Schema export tests: committed file matches, and sample reports validate."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from factories import make_report
from iota_report import export_schema
from iota_report.enums import CameraModel, ObservationResult, TimingMode
from iota_report.models import RollingShutterInputs

_SCHEMA_FILE = Path(__file__).parent.parent / "schema" / "iota-report.schema.json"
_D = datetime(2026, 7, 1, 5, 0, 0, tzinfo=UTC)
_R = datetime(2026, 7, 1, 5, 2, 0, tzinfo=UTC)


def test_committed_schema_matches_export() -> None:
    committed = json.loads(_SCHEMA_FILE.read_text())
    generated = export_schema()
    assert committed == generated, (
        "schema/iota-report.schema.json is stale; run "
        "`uv run python scripts/export_schema.py`"
    )


def test_schema_is_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(export_schema())


def test_maximal_report_validates_against_schema() -> None:
    report = make_report(
        camera_model=CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
        exposure="X2",
        timing_mode=TimingMode.AUTO_CORRECTED,
        disappearance_utc=_D,
        reappearance_utc=_R,
        rolling_shutter=RollingShutterInputs(
            night_shutter="NS1", star_y_at_d=100, star_y_at_r=120
        ),
        miss={"was_miss": "NO"},
        comments="Clean event, good SNR.",
        environment={
            "transparency": "CLEAR",
            "stability": "STEADY",
            "temperature_c": 12.5,
            "other_conditions": "light breeze",
            "interruptions": [
                {
                    "start_utc": "2026-07-01T05:10:00Z",
                    "end_utc": "2026-07-01T05:11:00Z",
                    "reason": "passing cloud",
                }
            ],
        },
    )
    validator = Draft202012Validator(export_schema())
    validator.validate(report.model_dump(mode="json"))


def test_minimal_report_validates_against_schema() -> None:
    report = make_report(result=ObservationResult.NEGATIVE)
    validator = Draft202012Validator(export_schema())
    validator.validate(report.model_dump(mode="json"))


def test_invalid_report_fails_schema() -> None:
    report = make_report(disappearance_utc=_D, reappearance_utc=_R)
    payload = report.model_dump(mode="json")
    payload["result"] = "NOT_A_RESULT"
    validator = Draft202012Validator(export_schema())
    with pytest.raises(ValidationError):
        validator.validate(payload)
