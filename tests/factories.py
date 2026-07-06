"""Test factories for building valid Report instances."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from iota_report import (
    CameraSetup,
    Environment,
    EventIdentity,
    EventTimings,
    Observer,
    Report,
    RollingShutterInputs,
    Station,
    Telescope,
    TimingMeasurement,
    TimingSetup,
)
from iota_report.enums import (
    CameraModel,
    CloudCondition,
    ExposureSetting,
    ObservationResult,
    OteProgram,
    Stability,
    StarCatalog,
    TelescopeType,
    TimeSource,
    TimingDevice,
    TimingMethod,
    TimingMode,
    VideoFormat,
)

_T0 = datetime(2026, 7, 1, 4, 55, 0, tzinfo=UTC)
_T1 = datetime(2026, 7, 1, 5, 30, 0, tzinfo=UTC)


def make_report(
    *,
    result: ObservationResult = ObservationResult.POSITIVE,
    camera_model: CameraModel = CameraModel.WATEC_910HX,
    exposure: ExposureSetting = ExposureSetting.X1,
    video_format: VideoFormat = VideoFormat.NTSC_EIA,
    timing_device: TimingDevice = TimingDevice.IOTA_VTI,
    ote_program: OteProgram = OteProgram.PYOTE,
    timing_mode: TimingMode = TimingMode.AUTO_CORRECTED,
    disappearance_utc: datetime | None = None,
    reappearance_utc: datetime | None = None,
    rolling_shutter: RollingShutterInputs | None = None,
    **overrides: Any,
) -> Report:
    """Build a valid Report with sensible defaults; override any group as needed."""
    disappearance = (
        TimingMeasurement(time_utc=disappearance_utc)
        if disappearance_utc is not None
        else None
    )
    reappearance = (
        TimingMeasurement(time_utc=reappearance_utc)
        if reappearance_utc is not None
        else None
    )

    data: dict[str, Any] = {
        "result": result,
        "event": EventIdentity(
            predicted_time_utc=datetime(2026, 7, 1, 5, 0, 0, tzinfo=UTC),
            asteroid_number=9721,
            asteroid_name="Phocaea",
            star_catalog=StarCatalog.TYC,
            star_number="1234-56789-1",
        ),
        "observer": Observer(
            names=["Jane Observer"],
            email="jane@example.com",
            home_location="Richmond, VA, US",
        ),
        "station": Station(
            location_name="Richmond, VA, US",
            latitude_deg=37.5,
            longitude_deg=-77.4,
            elevation_m=50.0,
        ),
        "telescope": Telescope(
            aperture_cm=20.0,
            focal_ratio=5.0,
            telescope_type=TelescopeType.NEWTONIAN,
        ),
        "timing_setup": TimingSetup(
            time_source=TimeSource.GPS_TIME_INSERTED,
            method=TimingMethod.VIDEO_FRAME_ANALYSIS,
            asteroid_visible=False,
            timing_device=timing_device,
            ote_program=ote_program,
        ),
        "camera": CameraSetup(
            camera_model=camera_model,
            video_format=video_format,
            exposure=exposure,
            rolling_shutter=rolling_shutter,
        ),
        "timings": EventTimings(
            timing_mode=timing_mode,
            start_observing_utc=_T0,
            stop_observing_utc=_T1,
            disappearance=disappearance,
            reappearance=reappearance,
        ),
        "environment": Environment(
            transparency=CloudCondition.CLEAR,
            stability=Stability.STEADY,
        ),
    }
    data.update(overrides)
    return Report.model_validate(data)
