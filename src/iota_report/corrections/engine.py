"""The timing-correction engine.

A faithful port of the Excel form's ``Corrections Calculations`` /
``Corrections Tables`` logic (excel-form-analysis §5). Producers use
:func:`apply_corrections`; the component functions are exposed for unit testing
and for building a live preview.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Literal

from iota_report.corrections.compatibility import (
    CompatibilityIssue,
    IncompatibleConfigurationError,
    InvalidCorrectionInputError,
    check_compatibility,
)
from iota_report.corrections.tables import (
    CAMDELAY_SUPPRESSING_OTES,
    CAMERA_DELAY_TABLE,
    ROLLING_SHUTTER_COEFFS,
    ROLLING_SHUTTER_Y_MAX,
    SELF_CORRECTING_CAMERAS,
    VTI_OFFSET_TABLE,
    ZERO_CORRECTION_FORMATS,
    video_family,
)
from iota_report.enums import (
    LABELS,
    CameraModel,
    ExposureSetting,
    NightShutter,
    OteProgram,
    TimingDevice,
    TimingMode,
    VideoFormat,
)

if TYPE_CHECKING:
    from iota_report.models import (
        CorrectedTimings,
        Report,
        RollingShutterInputs,
    )

_SECONDS_PER_DAY = 86400


def rolling_shutter_correction(
    night_shutter: NightShutter,
    y_position: int,
    video_format: VideoFormat,
    *,
    edge: Literal["D", "R"],
) -> float:
    """RunCam Night Eagle Astro rolling-shutter correction, seconds (§5.4).

    ``corr = -(a + b*Y) * 0.001``. Y is range-checked per family
    (NTSC 0-479, PAL 0-575), raising :class:`InvalidCorrectionInputError` when out
    of range. The PAL NS3 R-edge uses a distinct coefficient pair.

    Note: the design docstring folded an "additional VTI" layer into this
    function, but that layer depends on the OTE program and VTI device — which are
    not parameters here — so it lives in :func:`vti_offset` instead (see
    ``_additional_vti``). This function is the pure rolling-shutter polynomial.
    """
    family = video_family(video_format)
    y_max = ROLLING_SHUTTER_Y_MAX[family]
    if not 0 <= y_position <= y_max:
        raise InvalidCorrectionInputError(
            f"star Y position {y_position} out of range [0, {y_max}] for {family}"
        )
    a, b = ROLLING_SHUTTER_COEFFS[(night_shutter, family, edge)]
    return -(a + b * y_position) * 0.001


def _additional_vti(
    ote: OteProgram, timing_device: TimingDevice, is_pal: bool
) -> float:
    """RunCam Astro 'Additional VTI Corrections' layer (§5.4, F67:J75)."""
    if timing_device == TimingDevice.AFT_OFT_FLASH_TAG:
        return 0.0
    if ote == OteProgram.OCCULAR:
        return 0.02 if is_pal else 0.0167
    if ote in (OteProgram.R_OTE_WITH_CAMDELAY, OteProgram.R_OTE_WITHOUT_CAMDELAY):
        if timing_device in (TimingDevice.KIWI_OSD, TimingDevice.IOTA_VTI):
            return -0.02 if is_pal else -0.0167
        return 0.0
    return 0.0


def camera_delay(
    camera: CameraModel,
    exposure: ExposureSetting,
    video_format: VideoFormat,
    timing_device: TimingDevice,
    ote: OteProgram,
    *,
    edge: Literal["D", "R"],
    rolling_shutter: RollingShutterInputs | None = None,
) -> float:
    """Integration-delay camera correction, seconds (usually negative; §5.1).

    Zero when the timing device is an AFT/OFT Flash Tag or the OTE program already
    applied camera delay. RunCam Night Eagle Astro delegates to the per-edge
    rolling-shutter polynomial. Raises :class:`IncompatibleConfigurationError` for
    an out-of-matrix combination, or :class:`InvalidCorrectionInputError` when a
    RunCam Astro camera is missing its rolling-shutter inputs.
    """
    issues = check_compatibility(camera, exposure, ote, video_format)
    if issues:
        raise IncompatibleConfigurationError(issues)

    if (
        timing_device == TimingDevice.AFT_OFT_FLASH_TAG
        or ote in CAMDELAY_SUPPRESSING_OTES
    ):
        return 0.0

    if camera == CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO:
        if rolling_shutter is None:
            raise InvalidCorrectionInputError(
                "RUNCAM_NIGHT_EAGLE_ASTRO requires rolling_shutter inputs"
            )
        y = rolling_shutter.star_y_at_d if edge == "D" else rolling_shutter.star_y_at_r
        return rolling_shutter_correction(
            rolling_shutter.night_shutter, y, video_format, edge=edge
        )

    table = CAMERA_DELAY_TABLE.get(camera)
    if table is None:
        return 0.0  # catch-all camera: zero integration delay
    row = table.get(exposure)
    if row is None:
        raise IncompatibleConfigurationError(
            [
                CompatibilityIssue(
                    kind="exposure",
                    message=f"{LABELS[camera]} does not support {LABELS[exposure]} exposure",
                )
            ]
        )
    pal_value, ntsc_value = row
    value = pal_value if video_format == VideoFormat.PAL_CCIR else ntsc_value
    # A blank format column in the workbook evaluates to 0 in the arithmetic.
    return value if value is not None else 0.0


def vti_offset(
    ote: OteProgram,
    video_format: VideoFormat,
    camera: CameraModel,
    timing_device: TimingDevice,
) -> float:
    """VTI-hardware/analysis-program offset, seconds (§5.2)."""
    is_pal = video_format == VideoFormat.PAL_CCIR

    # RunCam Night Eagle Astro carries its own additional-VTI layer.
    if camera == CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO:
        return _additional_vti(ote, timing_device, is_pal)

    # RunCam (non-Astro) / Flash-Tag zero guard, unless the OTE is Occular.
    if (
        camera == CameraModel.RUNCAM_NIGHT_EAGLE
        or timing_device == TimingDevice.AFT_OFT_FLASH_TAG
    ) and ote != OteProgram.OCCULAR:
        return 0.0

    if ote == OteProgram.OCCULAR:
        return 0.02 if is_pal else 0.0

    # Self-correcting cameras zero the R-OTE-without-camdelay / PYOTE offsets.
    if (
        ote in (OteProgram.R_OTE_WITHOUT_CAMDELAY, OteProgram.PYOTE)
        and camera in SELF_CORRECTING_CAMERAS
    ):
        return 0.0

    pal, ntsc = VTI_OFFSET_TABLE[ote]
    return pal if is_pal else ntsc


def _near_midnight(raw: datetime | None, total_correction: float) -> bool:
    """True when a raw time is within |correction| + 2s of 00:00:00 UT (§5.6)."""
    if raw is None:
        return False
    seconds_of_day = (
        raw.hour * 3600 + raw.minute * 60 + raw.second + raw.microsecond / 1_000_000
    )
    distance = min(seconds_of_day, _SECONDS_PER_DAY - seconds_of_day)
    return distance <= abs(total_correction) + 2.0


@dataclass(frozen=True)
class CorrectionResult:
    corrected: CorrectedTimings
    applied: bool


def apply_corrections(report: Report) -> CorrectionResult:
    """Compute corrected D/R times for a report. Pure: does not mutate ``report``.

    - MANUALLY_CORRECTED mode, a self-correcting camera, or a blank OTE program:
      corrected times equal the entered times, all components zero, ``applied=False``.
    - AAV/ADVS video formats: total correction forced to zero (§5.3).
    - Otherwise: ``total = camera_delay + vti_offset`` per edge; corrected time is
      the raw time shifted by that total. Datetime arithmetic handles date rolls
      natively (no mod-86400 borrow logic).
    - ``near_midnight_review`` flags raw times within |correction| + 2s of midnight.
    - Raises :class:`IncompatibleConfigurationError` for out-of-matrix combos.
    """
    from iota_report.models import CorrectedTimings

    camera = report.camera.camera_model
    exposure = report.camera.exposure
    video_format = report.camera.video_format
    timing_device = report.timing_setup.timing_device
    ote = report.timing_setup.ote_program
    rolling_shutter = report.camera.rolling_shutter

    d_measurement = report.timings.disappearance
    r_measurement = report.timings.reappearance
    d_raw = d_measurement.time_utc if d_measurement is not None else None
    r_raw = r_measurement.time_utc if r_measurement is not None else None

    is_manual = (
        report.timings.timing_mode == TimingMode.MANUALLY_CORRECTED
        or camera in SELF_CORRECTING_CAMERAS
        or ote == OteProgram.NONE
    )
    if is_manual:
        return CorrectionResult(
            corrected=CorrectedTimings(
                disappearance_utc=d_raw,
                reappearance_utc=r_raw,
            ),
            applied=False,
        )

    issues = check_compatibility(camera, exposure, ote, video_format)
    if issues:
        raise IncompatibleConfigurationError(issues)

    if video_format in ZERO_CORRECTION_FORMATS:
        cam_d = cam_r = vti_d = vti_r = 0.0
    else:
        cam_d = camera_delay(
            camera,
            exposure,
            video_format,
            timing_device,
            ote,
            edge="D",
            rolling_shutter=rolling_shutter,
        )
        cam_r = camera_delay(
            camera,
            exposure,
            video_format,
            timing_device,
            ote,
            edge="R",
            rolling_shutter=rolling_shutter,
        )
        vti = vti_offset(ote, video_format, camera, timing_device)
        vti_d = vti_r = vti

    total_d = cam_d + vti_d
    total_r = cam_r + vti_r

    corrected_d = d_raw + timedelta(seconds=total_d) if d_raw is not None else None
    corrected_r = r_raw + timedelta(seconds=total_r) if r_raw is not None else None

    near_midnight = _near_midnight(d_raw, total_d) or _near_midnight(r_raw, total_r)

    return CorrectionResult(
        corrected=CorrectedTimings(
            disappearance_utc=corrected_d,
            reappearance_utc=corrected_r,
            camera_delay_d_s=cam_d,
            camera_delay_r_s=cam_r,
            vti_offset_d_s=vti_d,
            vti_offset_r_s=vti_r,
            total_correction_d_s=total_d,
            total_correction_r_s=total_r,
            near_midnight_review=near_midnight,
        ),
        applied=True,
    )
