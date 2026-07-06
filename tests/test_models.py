"""Model validation tests: cross-field validators (both directions), UTC policy,
enum round-trips, extra-key rejection."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from factories import make_report
from iota_report import Report
from iota_report.enums import (
    CameraModel,
    ExposureSetting,
    ObservationResult,
    StarCatalog,
    TimingMode,
    VideoFormat,
)
from iota_report.models import RollingShutterInputs

_D = datetime(2026, 7, 1, 5, 0, 0, tzinfo=UTC)
_R = datetime(2026, 7, 1, 5, 2, 0, tzinfo=UTC)


def test_positive_requires_disappearance_and_reappearance() -> None:
    with pytest.raises(ValidationError, match="POSITIVE result requires"):
        make_report(
            result=ObservationResult.POSITIVE,
            disappearance_utc=None,
            reappearance_utc=None,
        )


def test_positive_with_both_times_ok() -> None:
    report = make_report(disappearance_utc=_D, reappearance_utc=_R)
    assert report.result == ObservationResult.POSITIVE


def test_negative_without_times_ok() -> None:
    report = make_report(result=ObservationResult.NEGATIVE)
    assert report.timings.disappearance is None


def test_runcam_astro_auto_requires_rolling_shutter() -> None:
    with pytest.raises(ValidationError, match="rolling_shutter"):
        make_report(
            camera_model=CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
            exposure=ExposureSetting.X2,
            timing_mode=TimingMode.AUTO_CORRECTED,
            disappearance_utc=_D,
            reappearance_utc=_R,
            rolling_shutter=None,
        )


def test_runcam_astro_auto_with_rolling_shutter_ok() -> None:
    report = make_report(
        camera_model=CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
        exposure=ExposureSetting.X2,
        timing_mode=TimingMode.AUTO_CORRECTED,
        disappearance_utc=_D,
        reappearance_utc=_R,
        rolling_shutter=RollingShutterInputs(
            night_shutter="NS1", star_y_at_d=100, star_y_at_r=100
        ),
    )
    assert report.camera.rolling_shutter is not None


def test_camera_other_requires_camera_other_text() -> None:
    with pytest.raises(ValidationError, match="camera_other"):
        make_report(
            camera_model=CameraModel.OTHER,
            timing_mode=TimingMode.MANUALLY_CORRECTED,
            disappearance_utc=_D,
            reappearance_utc=_R,
        )


def test_camera_other_with_text_ok() -> None:
    report = make_report(
        camera_model=CameraModel.OTHER,
        timing_mode=TimingMode.MANUALLY_CORRECTED,
        disappearance_utc=_D,
        reappearance_utc=_R,
        camera={
            "camera_model": "OTHER",
            "camera_other": "Homebrew EMCCD",
            "video_format": "NTSC_EIA",
            "exposure": "X1",
        },
    )
    assert report.camera.camera_other == "Homebrew EMCCD"


def test_stop_must_be_after_start() -> None:
    with pytest.raises(ValidationError, match="stop_observing_utc must be after"):
        make_report(
            disappearance_utc=_D,
            reappearance_utc=_R,
            timings={
                "timing_mode": "AUTO_CORRECTED",
                "start_observing_utc": "2026-07-01T05:30:00Z",
                "stop_observing_utc": "2026-07-01T04:55:00Z",
                "disappearance": {"time_utc": "2026-07-01T05:00:00Z"},
                "reappearance": {"time_utc": "2026-07-01T05:02:00Z"},
            },
        )


def test_self_correcting_camera_forbids_auto_mode() -> None:
    with pytest.raises(ValidationError, match="self-correcting"):
        make_report(
            camera_model=CameraModel.G_STAR,
            timing_mode=TimingMode.AUTO_CORRECTED,
            disappearance_utc=_D,
            reappearance_utc=_R,
        )


def test_self_correcting_camera_allows_manual_mode() -> None:
    report = make_report(
        camera_model=CameraModel.G_STAR,
        timing_mode=TimingMode.MANUALLY_CORRECTED,
        disappearance_utc=_D,
        reappearance_utc=_R,
    )
    assert report.timings.timing_mode == TimingMode.MANUALLY_CORRECTED


def test_naive_datetime_rejected() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        make_report(
            disappearance_utc=_D,
            reappearance_utc=_R,
            timings={
                "timing_mode": "AUTO_CORRECTED",
                "start_observing_utc": "2026-07-01T04:55:00",  # naive
                "stop_observing_utc": "2026-07-01T05:30:00Z",
                "disappearance": {"time_utc": "2026-07-01T05:00:00Z"},
                "reappearance": {"time_utc": "2026-07-01T05:02:00Z"},
            },
        )


def test_non_utc_offset_rejected() -> None:
    with pytest.raises(ValidationError, match="must be UTC"):
        make_report(
            disappearance_utc=_D,
            reappearance_utc=_R,
            timings={
                "timing_mode": "AUTO_CORRECTED",
                "start_observing_utc": "2026-07-01T04:55:00-05:00",
                "stop_observing_utc": "2026-07-01T05:30:00Z",
                "disappearance": {"time_utc": "2026-07-01T05:00:00Z"},
                "reappearance": {"time_utc": "2026-07-01T05:02:00Z"},
            },
        )


def test_utc_serialization_is_z_suffixed_millis() -> None:
    report = make_report(disappearance_utc=_D, reappearance_utc=_R)
    dumped = report.model_dump(mode="json")
    assert dumped["timings"]["disappearance"]["time_utc"] == "2026-07-01T05:00:00.000Z"


def test_extra_keys_forbidden() -> None:
    report = make_report(disappearance_utc=_D, reappearance_utc=_R)
    payload = report.model_dump(mode="json")
    payload["unexpected_field"] = "boom"
    with pytest.raises(
        ValidationError, match=r"Extra inputs|extra_forbidden|not permitted"
    ):
        Report.model_validate(payload)


def test_enum_round_trip() -> None:
    report = make_report(disappearance_utc=_D, reappearance_utc=_R)
    payload = report.model_dump(mode="json")
    assert payload["event"]["star_catalog"] == "TYC"
    assert payload["camera"]["video_format"] == "NTSC_EIA"
    round_tripped = Report.model_validate(payload)
    assert round_tripped.event.star_catalog == StarCatalog.TYC
    assert round_tripped.camera.video_format == VideoFormat.NTSC_EIA


def test_star_catalog_legacy_values() -> None:
    # 1B / 1N members keep their Excel string values.
    assert StarCatalog.B1.value == "1B"
    assert StarCatalog.N1.value == "1N"


def test_schema_version_default_present() -> None:
    report = make_report(disappearance_utc=_D, reappearance_utc=_R)
    assert report.schema_version
