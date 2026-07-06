"""Golden-vector runner for the correction engine.

Expected values in ``golden/corrections.json`` are transcribed from the Excel
form's documented tables/formulas (excel-form-analysis §5-6), independent of the
engine implementation. This test drives each engine entry point and compares.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from factories import make_report
from iota_report import (
    apply_corrections,
    camera_delay,
    check_compatibility,
    rolling_shutter_correction,
    vti_offset,
)
from iota_report.corrections import IncompatibleConfigurationError
from iota_report.enums import (
    CameraModel,
    ExposureSetting,
    NightShutter,
    ObservationResult,
    OteProgram,
    TimingDevice,
    TimingMode,
    VideoFormat,
)
from iota_report.models import RollingShutterInputs

_GOLDEN = json.loads(
    (Path(__file__).parent / "golden" / "corrections.json").read_text()
)

_ABS = 1e-9


def _id(vector: dict[str, Any]) -> str:
    return vector["name"]


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


@pytest.mark.parametrize("vector", _GOLDEN["camera_delay"], ids=_id)
def test_camera_delay_golden(vector: dict[str, Any]) -> None:
    rs = vector.get("rolling_shutter")
    rolling = RollingShutterInputs(**rs) if rs else None
    kwargs = {
        "camera": CameraModel(vector["camera"]),
        "exposure": ExposureSetting(vector["exposure"]),
        "video_format": VideoFormat(vector["video_format"]),
        "timing_device": TimingDevice(vector["timing_device"]),
        "ote": OteProgram(vector["ote"]),
        "edge": vector["edge"],
        "rolling_shutter": rolling,
    }
    expect = vector["expect"]
    if isinstance(expect, dict) and expect.get("raises"):
        with pytest.raises(IncompatibleConfigurationError):
            camera_delay(**kwargs)
    else:
        assert camera_delay(**kwargs) == pytest.approx(expect, abs=_ABS)


@pytest.mark.parametrize("vector", _GOLDEN["vti_offset"], ids=_id)
def test_vti_offset_golden(vector: dict[str, Any]) -> None:
    result = vti_offset(
        OteProgram(vector["ote"]),
        VideoFormat(vector["video_format"]),
        CameraModel(vector["camera"]),
        TimingDevice(vector["timing_device"]),
    )
    assert result == pytest.approx(vector["expect"], abs=_ABS)


@pytest.mark.parametrize("vector", _GOLDEN["rolling_shutter"], ids=_id)
def test_rolling_shutter_golden(vector: dict[str, Any]) -> None:
    kwargs = {
        "night_shutter": NightShutter(vector["night_shutter"]),
        "y_position": vector["y_position"],
        "video_format": VideoFormat(vector["video_format"]),
        "edge": vector["edge"],
    }
    expect = vector["expect"]
    if isinstance(expect, dict) and expect.get("raises"):
        with pytest.raises(ValueError):
            rolling_shutter_correction(**kwargs)
    else:
        assert rolling_shutter_correction(**kwargs) == pytest.approx(expect, abs=_ABS)


@pytest.mark.parametrize("vector", _GOLDEN["apply"], ids=_id)
def test_apply_corrections_golden(vector: dict[str, Any]) -> None:
    rs = vector.get("rolling_shutter")
    rolling = RollingShutterInputs(**rs) if rs else None
    report = make_report(
        result=ObservationResult(vector["result"]),
        camera_model=CameraModel(vector["camera"]),
        exposure=ExposureSetting(vector["exposure"]),
        video_format=VideoFormat(vector["video_format"]),
        timing_device=TimingDevice(vector["timing_device"]),
        ote_program=OteProgram(vector["ote"]),
        timing_mode=TimingMode(vector["timing_mode"]),
        disappearance_utc=_parse_dt(vector["d_raw_utc"])
        if vector.get("d_raw_utc")
        else None,
        reappearance_utc=_parse_dt(vector["r_raw_utc"])
        if vector.get("r_raw_utc")
        else None,
        rolling_shutter=rolling,
    )

    expect = vector["expect"]
    if expect.get("raises"):
        with pytest.raises(IncompatibleConfigurationError):
            apply_corrections(report)
        return

    result = apply_corrections(report)
    corrected = result.corrected

    if "applied" in expect:
        assert result.applied == expect["applied"]
    for field in (
        "camera_delay_d_s",
        "camera_delay_r_s",
        "vti_offset_d_s",
        "total_correction_d_s",
        "total_correction_r_s",
    ):
        if field in expect:
            assert getattr(corrected, field) == pytest.approx(expect[field], abs=_ABS)
    if "near_midnight_review" in expect:
        assert corrected.near_midnight_review == expect["near_midnight_review"]
    if "corrected_d_utc" in expect:
        assert corrected.disappearance_utc is not None
        delta = abs(corrected.disappearance_utc - _parse_dt(expect["corrected_d_utc"]))
        assert delta < timedelta(milliseconds=2)
    if "corrected_r_utc" in expect:
        assert corrected.reappearance_utc is not None
        delta = abs(corrected.reappearance_utc - _parse_dt(expect["corrected_r_utc"]))
        assert delta < timedelta(milliseconds=2)


@pytest.mark.parametrize("vector", _GOLDEN["check_compatibility"], ids=_id)
def test_check_compatibility_golden(vector: dict[str, Any]) -> None:
    issues = check_compatibility(
        CameraModel(vector["camera"]),
        ExposureSetting(vector["exposure"]),
        OteProgram(vector["ote"]),
        VideoFormat(vector["video_format"]),
    )
    assert sorted(issue.kind for issue in issues) == sorted(vector["expect_kinds"])
