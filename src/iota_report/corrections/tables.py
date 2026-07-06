"""Timing-correction lookup tables, transcribed from the IOTA Excel form.

Every constant here is a faithful port of a ``Corrections Tables`` /
``Corrections Calculations`` range in ``NorthAmerica_AstReportForm_V5.6.12r.xlsx``,
as documented in ``features/report-overhaul/excel-form-analysis.md`` §5-6. The
section/table each constant comes from is cited inline. These change only with a
package release.

Camera-delay table values are ``(pal_ccir_seconds, ntsc_eia_seconds)``; ``None``
marks a format the camera does not support (e.g. NTSC-only cameras have no PAL
column), matching the blank cell in the workbook.
"""

from __future__ import annotations

from typing import Literal

from iota_report.enums import (
    CameraModel,
    ExposureSetting,
    NightShutter,
    OteProgram,
    VideoFormat,
)

# --- Field durations (§6.1) ---------------------------------------------------
# NTSC/EIA field = 1/59.94 s; PAL/CCIR field = 1/50 s.
FIELD_DURATION_S: dict[VideoFormat, float] = {
    VideoFormat.NTSC_EIA: 0.0167,
    VideoFormat.PAL_CCIR: 0.02,
}

# --- Per-camera integration-delay tables (§6.2) -------------------------------
# camera -> exposure -> (pal_ccir_s, ntsc_eia_s)

_WATEC_120N: dict[ExposureSetting, tuple[float | None, float | None]] = {
    ExposureSetting.X1: (-0.04, -0.0334),
    ExposureSetting.X2: (-0.06, -0.0501),
    ExposureSetting.X4: (-0.10, -0.0834),
    ExposureSetting.X8: (-0.18, -0.1502),
    ExposureSetting.X16: (-0.34, -0.2836),
    ExposureSetting.X32: (-0.66, -0.5506),
    ExposureSetting.X64: (-1.30, -1.0844),
    ExposureSetting.X128: (-2.58, -2.1522),
    ExposureSetting.X256: (-5.14, -4.2876),
    ExposureSetting.X512: (-10.26, -8.5586),
}

_WATEC_910: dict[ExposureSetting, tuple[float | None, float | None]] = {
    ExposureSetting.X1: (-0.02, -0.0167),
    ExposureSetting.X2: (-0.04, -0.0334),
    ExposureSetting.X4: (-0.08, -0.0667),
    ExposureSetting.X8: (-0.16, -0.1335),
    ExposureSetting.X16: (-0.32, -0.2669),
    ExposureSetting.X32: (-0.64, -0.5339),
    ExposureSetting.X64: (-1.28, -1.0677),
    ExposureSetting.X128: (-2.56, -2.1355),
    ExposureSetting.X256: (-5.08, -4.2376),
}

_PC165_DNR: dict[ExposureSetting, tuple[float | None, float | None]] = {
    ExposureSetting.X1: (None, -0.0167),
    ExposureSetting.X2: (None, -0.0334),
    ExposureSetting.X4: (None, -0.0667),
    ExposureSetting.X8: (None, -0.1335),
    ExposureSetting.X16: (None, -0.2669),
    ExposureSetting.X32: (None, -0.5339),
    ExposureSetting.X64: (None, -1.0677),
    ExposureSetting.X128: (None, -2.1355),
    ExposureSetting.X256: (None, -4.2709),
}

_MINTRON: dict[ExposureSetting, tuple[float | None, float | None]] = {
    ExposureSetting.X1: (0.0, 0.0),
    ExposureSetting.X2: (-0.02, -0.0167),
    ExposureSetting.X4: (-0.06, -0.0501),
    ExposureSetting.X6: (-0.10, -0.0834),
    ExposureSetting.X8: (-0.14, -0.1168),
    ExposureSetting.X12: (-0.18, -0.1502),
    ExposureSetting.X16: (-0.30, -0.2503),
    ExposureSetting.X24: (-0.46, -0.3837),
    ExposureSetting.X32: (-0.62, -0.5172),
    ExposureSetting.X48: (-0.94, -0.7841),
    ExposureSetting.X64: (-1.26, -1.0511),
    ExposureSetting.X96: (-1.86, -1.5516),
    ExposureSetting.X128: (-2.54, -2.1188),
}

_MALLINCAM: dict[ExposureSetting, tuple[float | None, float | None]] = {
    ExposureSetting.X1: (-0.02, -0.0167),
    ExposureSetting.X2: (-0.04, -0.0334),
    ExposureSetting.X4: (-0.08, -0.0667),
    ExposureSetting.X6: (-0.12, -0.1001),
    ExposureSetting.X8: (-0.16, -0.1335),
    ExposureSetting.X12: (-0.20, -0.1668),
    ExposureSetting.X16: (-0.32, -0.2669),
    ExposureSetting.X24: (-0.48, -0.4004),
    ExposureSetting.X32: (-0.64, -0.5339),
    ExposureSetting.X48: (-0.96, -0.8008),
    ExposureSetting.X64: (-1.28, -1.0677),
    ExposureSetting.X96: (-1.88, -1.5682),
    ExposureSetting.X128: (-2.56, -2.1355),
}

_SAMSUNG: dict[ExposureSetting, tuple[float | None, float | None]] = {
    ExposureSetting.X1: (None, -0.0334),
    ExposureSetting.X2: (None, -0.0501),
    ExposureSetting.X4: (None, -0.0834),
    ExposureSetting.X6: (None, -0.1168),
    ExposureSetting.X8: (None, -0.1502),
    ExposureSetting.X10: (None, -0.1835),
    ExposureSetting.X12: (None, -0.2169),
    ExposureSetting.X14: (None, -0.2503),
    ExposureSetting.X16: (None, -0.2836),
    ExposureSetting.X24: (None, -0.4171),
    ExposureSetting.X32: (None, -0.5506),
    ExposureSetting.X64: (None, -1.0844),
    ExposureSetting.X128: (None, -2.1522),
    ExposureSetting.X256: (None, -4.2876),
    ExposureSetting.X512: (None, -8.5586),
}

# RunCam Night Eagle (non-Astro): flat 1x delay, no rolling-shutter correction (§6.2 B106).
_RUNCAM_NIGHT_EAGLE: dict[ExposureSetting, tuple[float | None, float | None]] = {
    ExposureSetting.X1: (-0.02, -0.0167),
}

CAMERA_DELAY_TABLE: dict[
    CameraModel, dict[ExposureSetting, tuple[float | None, float | None]]
] = {
    CameraModel.WATEC_120N: _WATEC_120N,
    CameraModel.WATEC_120N_PLUS: _WATEC_120N,
    CameraModel.WATEC_910HX: _WATEC_910,
    CameraModel.WATEC_910BD: _WATEC_910,
    CameraModel.PC165_DNR: _PC165_DNR,
    CameraModel.MINTRON_12V1C_EX: _MINTRON,
    CameraModel.MALLINCAM: _MALLINCAM,
    CameraModel.SAMSUNG_SBC_2000: _SAMSUNG,
    CameraModel.RUNCAM_NIGHT_EAGLE: _RUNCAM_NIGHT_EAGLE,
}
# Every other camera has zero integration delay (§6.2 B108 catch-all).

# --- VTI offset by OTE program (§5.2, Corrections Calculations Q44:S50) --------
# Base (pal_ccir_s, ntsc_eia_s). The conditional guards (RunCam/Flash-Tag zeroing,
# self-correcting-camera zeroing, and the Occular RunCam-Astro NTSC special case)
# live in engine.vti_offset, which is what callers use.
VTI_OFFSET_TABLE: dict[OteProgram, tuple[float, float]] = {
    OteProgram.NONE: (0.0, 0.0),
    OteProgram.MANUAL: (0.0, 0.0),
    OteProgram.OTHER: (0.0, 0.0),
    OteProgram.AOTA_WITH_CAMDELAY: (0.0, 0.0),
    OteProgram.OCCULAR: (0.02, 0.0),
    OteProgram.R_OTE_WITH_CAMDELAY: (0.0, 0.0),
    OteProgram.R_OTE_WITHOUT_CAMDELAY: (-0.02, -0.0167),
    OteProgram.PYOTE: (-0.02, -0.0167),
}

# --- RunCam Night Eagle Astro rolling-shutter polynomials (§5.4) ---------------
# corr = -(a + b*Y) * 0.001 seconds, keyed by (night shutter, video family, edge).
# D and R are identical except (NS3, PAL, R), which uses the R-variant coefficients.
_VideoFamily = Literal["NTSC", "PAL"]

ROLLING_SHUTTER_COEFFS: dict[
    tuple[NightShutter, _VideoFamily, Literal["D", "R"]], tuple[float, float]
] = {
    (NightShutter.NS1, "NTSC", "D"): (69.03, -0.066744),
    (NightShutter.NS1, "NTSC", "R"): (69.03, -0.066744),
    (NightShutter.NS2, "NTSC", "D"): (102.68, -0.067282),
    (NightShutter.NS2, "NTSC", "R"): (102.68, -0.067282),
    (NightShutter.NS3, "NTSC", "D"): (169.24, -0.066563),
    (NightShutter.NS3, "NTSC", "R"): (169.24, -0.066563),
    (NightShutter.NS1, "PAL", "D"): (74.24, -0.063143),
    (NightShutter.NS1, "PAL", "R"): (74.24, -0.063143),
    (NightShutter.NS2, "PAL", "D"): (114.12, -0.062652),
    (NightShutter.NS2, "PAL", "R"): (114.12, -0.062652),
    (NightShutter.NS3, "PAL", "D"): (194.14, -0.062402),
    (NightShutter.NS3, "PAL", "R"): (194.94, -0.062463),  # R-variant coefficients
}

# RunCam Astro Y-position pixel ranges per video family (§2.6, §5.4).
ROLLING_SHUTTER_Y_MAX: dict[_VideoFamily, int] = {"NTSC": 479, "PAL": 575}

# Exposure -> night shutter mapping for RunCam Astro (§5.4: 2x/4x/8x -> NS1/NS2/NS3).
EXPOSURE_TO_NIGHT_SHUTTER: dict[ExposureSetting, NightShutter] = {
    ExposureSetting.X2: NightShutter.NS1,
    ExposureSetting.X4: NightShutter.NS2,
    ExposureSetting.X8: NightShutter.NS3,
}

# --- Camera classification frozensets -----------------------------------------
# Self-correcting cameras (§5.7): observer enters already-corrected times; the
# engine adds zero and the DATA row label flips to "Manually-Corrected".
SELF_CORRECTING_CAMERAS: frozenset[CameraModel] = frozenset(
    {
        CameraModel.QHY_174_GPS,
        CameraModel.OTHER,
        CameraModel.VISUAL,
        CameraModel.PHOTOMETER,
        CameraModel.CCD_DRIFT_SCAN,
        CameraModel.FLEA3_03S1_ADVS,
        CameraModel.FLEA3_03S3_ADVS,
        CameraModel.FLEA3_28S4M_ADVS,
        CameraModel.GRASSHOPPER_EXPRESS_ADVS,
        CameraModel.G_STAR,
        CameraModel.ASTRID,
    }
)

# Video formats whose recorded time is already the sample centre (§5.3): no
# correction is applied at any exposure.
ZERO_CORRECTION_FORMATS: frozenset[VideoFormat] = frozenset(
    {VideoFormat.AAV_NTSC, VideoFormat.AAV_PAL, VideoFormat.ADVS}
)

# OTE programs that already applied camera delay themselves (§5.1): camera delay
# is suppressed to avoid double-correcting.
CAMDELAY_SUPPRESSING_OTES: frozenset[OteProgram] = frozenset(
    {
        OteProgram.AOTA_WITH_CAMDELAY,
        OteProgram.R_OTE_WITH_CAMDELAY,
        OteProgram.MANUAL,
        OteProgram.OTHER,
    }
)

# --- Compatibility matrix (§5.8 / §6.4, _CamExpArrayTable) ---------------------
# camera -> allowed exposures. For table cameras this mirrors the delay-table keys
# (an exposure with no tabulated delay is out of matrix). Self-correcting and
# catch-all cameras handle only a 1x-equivalent; RunCam Astro allows 2x/4x/8x.
_ALL_EXPOSURES = frozenset(ExposureSetting)


def _exposures_for(camera: CameraModel) -> frozenset[ExposureSetting]:
    if camera in CAMERA_DELAY_TABLE:
        return frozenset(CAMERA_DELAY_TABLE[camera])
    return frozenset({ExposureSetting.X1})


COMPATIBILITY_EXPOSURES: dict[CameraModel, frozenset[ExposureSetting]] = {
    **{cam: _exposures_for(cam) for cam in CameraModel},
    CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO: frozenset(
        {ExposureSetting.X2, ExposureSetting.X4, ExposureSetting.X8}
    ),
}

_ALL_OTES = frozenset(OteProgram)

# camera -> allowed OTE programs. The only documented restriction (§6.4) is that
# QHY 174 GPS and ASTRID cannot apply R-OTE-with-camera-delay.
COMPATIBILITY_OTES: dict[CameraModel, frozenset[OteProgram]] = {
    CameraModel.QHY_174_GPS: _ALL_OTES - {OteProgram.R_OTE_WITH_CAMDELAY},
    CameraModel.ASTRID: _ALL_OTES - {OteProgram.R_OTE_WITH_CAMDELAY},
}
