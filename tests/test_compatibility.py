"""Compatibility-matrix enforcement tests (§5.8 / §6.4)."""

from __future__ import annotations

from iota_report import check_compatibility
from iota_report.corrections import CompatibilityIssue, IncompatibleConfigurationError
from iota_report.enums import CameraModel, ExposureSetting, OteProgram, VideoFormat


def test_valid_combo_has_no_issues() -> None:
    issues = check_compatibility(
        CameraModel.WATEC_120N,
        ExposureSetting.X8,
        OteProgram.PYOTE,
        VideoFormat.NTSC_EIA,
    )
    assert issues == []


def test_out_of_matrix_exposure_flagged() -> None:
    issues = check_compatibility(
        CameraModel.WATEC_120N,
        ExposureSetting.X6,
        OteProgram.PYOTE,
        VideoFormat.NTSC_EIA,
    )
    assert [i.kind for i in issues] == ["exposure"]


def test_qhy_cannot_apply_rote_with_camdelay() -> None:
    issues = check_compatibility(
        CameraModel.QHY_174_GPS,
        ExposureSetting.X1,
        OteProgram.R_OTE_WITH_CAMDELAY,
        VideoFormat.NTSC_EIA,
    )
    assert [i.kind for i in issues] == ["ote"]


def test_multiple_issues_reported_together() -> None:
    issues = check_compatibility(
        CameraModel.QHY_174_GPS,
        ExposureSetting.X6,
        OteProgram.R_OTE_WITH_CAMDELAY,
        VideoFormat.NTSC_EIA,
    )
    assert sorted(i.kind for i in issues) == ["exposure", "ote"]


def test_runcam_astro_exposures_restricted_to_ns_series() -> None:
    for good in (ExposureSetting.X2, ExposureSetting.X4, ExposureSetting.X8):
        assert (
            check_compatibility(
                CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
                good,
                OteProgram.PYOTE,
                VideoFormat.NTSC_EIA,
            )
            == []
        )
    bad = check_compatibility(
        CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO,
        ExposureSetting.X16,
        OteProgram.PYOTE,
        VideoFormat.NTSC_EIA,
    )
    assert [i.kind for i in bad] == ["exposure"]


def test_incompatible_error_carries_issues() -> None:
    issues = [CompatibilityIssue(kind="exposure", message="nope")]
    error = IncompatibleConfigurationError(issues)
    assert error.issues == issues
    assert "nope" in str(error)
