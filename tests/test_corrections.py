"""Unit tests for individual correction component functions.

These complement the golden vectors with targeted behavioral checks (guards,
edge cases, purity) that are clearer as direct assertions.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from factories import make_report
from iota_report import (
    apply_corrections,
    camera_delay,
    rolling_shutter_correction,
    vti_offset,
)
from iota_report.corrections import (
    CorrectionError,
    IncompatibleConfigurationError,
    InvalidCorrectionInputError,
)
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

_D = datetime(2026, 7, 1, 5, 0, 0, tzinfo=UTC)
_R = datetime(2026, 7, 1, 5, 2, 0, tzinfo=UTC)


def test_camera_delay_suppressed_by_camdelay_otes() -> None:
    for ote in (
        OteProgram.AOTA_WITH_CAMDELAY,
        OteProgram.R_OTE_WITH_CAMDELAY,
        OteProgram.MANUAL,
        OteProgram.OTHER,
    ):
        assert (
            camera_delay(
                CameraModel.WATEC_120N,
                ExposureSetting.X8,
                VideoFormat.NTSC_EIA,
                TimingDevice.IOTA_VTI,
                ote,
                edge="D",
            )
            == 0.0
        )


def test_camera_delay_pal_column_only_for_pal_ccir() -> None:
    # Excel selects the PAL column only when format == PAL/CCIR exactly.
    pal = camera_delay(
        CameraModel.WATEC_120N,
        ExposureSetting.X1,
        VideoFormat.PAL_CCIR,
        TimingDevice.IOTA_VTI,
        OteProgram.PYOTE,
        edge="D",
    )
    ntsc = camera_delay(
        CameraModel.WATEC_120N,
        ExposureSetting.X1,
        VideoFormat.NTSC_EIA,
        TimingDevice.IOTA_VTI,
        OteProgram.PYOTE,
        edge="D",
    )
    assert pal == pytest.approx(-0.04)
    assert ntsc == pytest.approx(-0.0334)


def test_camera_delay_runcam_astro_requires_rolling_shutter() -> None:
    with pytest.raises(ValueError, match="rolling_shutter"):
        camera_delay(
            CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
            ExposureSetting.X2,
            VideoFormat.NTSC_EIA,
            TimingDevice.IOTA_VTI,
            OteProgram.PYOTE,
            edge="D",
        )


def test_camera_delay_runcam_astro_uses_per_edge_y() -> None:
    rs = RollingShutterInputs(
        night_shutter=NightShutter.NS1, star_y_at_d=0, star_y_at_r=240
    )
    d = camera_delay(
        CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
        ExposureSetting.X2,
        VideoFormat.NTSC_EIA,
        TimingDevice.IOTA_VTI,
        OteProgram.PYOTE,
        edge="D",
        rolling_shutter=rs,
    )
    r = camera_delay(
        CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
        ExposureSetting.X2,
        VideoFormat.NTSC_EIA,
        TimingDevice.IOTA_VTI,
        OteProgram.PYOTE,
        edge="R",
        rolling_shutter=rs,
    )
    assert d == pytest.approx(-0.06903)
    assert r == pytest.approx(-0.05301144)


def test_rolling_shutter_y_out_of_range_raises_typed_error() -> None:
    with pytest.raises(InvalidCorrectionInputError) as excinfo:
        rolling_shutter_correction(
            NightShutter.NS1, 480, VideoFormat.NTSC_EIA, edge="D"
        )
    # Catchable via the package error family and the ValueError base.
    assert isinstance(excinfo.value, CorrectionError)
    assert isinstance(excinfo.value, ValueError)


def test_engine_errors_share_one_family() -> None:
    # Both engine error types resolve through CorrectionError so a caller can
    # catch the whole family with a single except clause.
    assert issubclass(IncompatibleConfigurationError, CorrectionError)
    assert issubclass(InvalidCorrectionInputError, CorrectionError)


def test_camera_delay_missing_rolling_shutter_is_typed() -> None:
    with pytest.raises(CorrectionError):
        camera_delay(
            CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
            ExposureSetting.X2,
            VideoFormat.NTSC_EIA,
            TimingDevice.IOTA_VTI,
            OteProgram.PYOTE,
            edge="D",
        )


def test_rolling_shutter_pal_ns3_r_variant_differs_from_d() -> None:
    d = rolling_shutter_correction(
        NightShutter.NS3, 240, VideoFormat.PAL_CCIR, edge="D"
    )
    r = rolling_shutter_correction(
        NightShutter.NS3, 240, VideoFormat.PAL_CCIR, edge="R"
    )
    assert d != r
    assert d == pytest.approx(-0.17916352)
    assert r == pytest.approx(-0.17994888)


def test_rolling_shutter_ntsc_d_equals_r() -> None:
    d = rolling_shutter_correction(
        NightShutter.NS2, 100, VideoFormat.NTSC_EIA, edge="D"
    )
    r = rolling_shutter_correction(
        NightShutter.NS2, 100, VideoFormat.NTSC_EIA, edge="R"
    )
    assert d == r


def test_vti_offset_occular_runcam_astro_special_case() -> None:
    assert vti_offset(
        OteProgram.OCCULAR,
        VideoFormat.NTSC_EIA,
        CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
        TimingDevice.IOTA_VTI,
    ) == pytest.approx(0.0167)


def test_apply_corrections_does_not_mutate_report() -> None:
    report = make_report(disappearance_utc=_D, reappearance_utc=_R)
    assert report.timings.corrected is None
    apply_corrections(report)
    assert report.timings.corrected is None  # pure function


def test_apply_corrections_incompatible_raises_with_issues() -> None:
    report = make_report(
        camera_model=CameraModel.WATEC_120N,
        exposure=ExposureSetting.X6,
        disappearance_utc=_D,
        reappearance_utc=_R,
    )
    with pytest.raises(IncompatibleConfigurationError) as excinfo:
        apply_corrections(report)
    assert excinfo.value.issues
    assert excinfo.value.issues[0].kind == "exposure"


def test_apply_corrections_negative_only_disappearance() -> None:
    report = make_report(
        result=ObservationResult.NEGATIVE,
        camera_model=CameraModel.WATEC_120N,
        exposure=ExposureSetting.X1,
        timing_mode=TimingMode.AUTO_CORRECTED,
        disappearance_utc=_D,
        reappearance_utc=None,
    )
    result = apply_corrections(report)
    assert result.corrected.disappearance_utc is not None
    assert result.corrected.reappearance_utc is None
