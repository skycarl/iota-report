"""Pydantic v2 models for the portable occultation report.

The top-level model is :class:`Report`. Every sub-model forbids unknown keys
(``extra="forbid"``) because a portable format must surface typos rather than
silently drop them.

Datetime policy (design §A.2): every time is a full ISO-8601 UTC datetime. A
validator rejects naive or non-UTC values and normalizes to UTC; JSON
serialization is ``Z``-suffixed with millisecond precision. This removes the
Excel form's date/time-of-day split and its midnight-wrap fragility.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    PlainSerializer,
    model_validator,
)

from iota_report.corrections.tables import SELF_CORRECTING_CAMERAS
from iota_report.enums import (
    CameraModel,
    CloudCondition,
    Datum,
    ExposureSetting,
    NightShutter,
    ObservationResult,
    OteProgram,
    PassDirection,
    Stability,
    StarCatalog,
    TelescopeType,
    TimeSource,
    TimingDevice,
    TimingMethod,
    TimingMode,
    VideoFormat,
    YesNoMaybe,
)
from iota_report.schema import SCHEMA_VERSION


def _ensure_utc(value: datetime) -> datetime:
    """Reject naive/non-UTC datetimes and normalize to a UTC-aware value."""
    if value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware and UTC")
    offset = value.utcoffset()
    if offset is None or offset != timedelta(0):
        raise ValueError("datetime must be UTC (offset +00:00)")
    return value.astimezone(UTC)


def _serialize_utc(value: datetime) -> str:
    """Serialize as a ``Z``-suffixed ISO-8601 string with millisecond precision."""
    aware = value.astimezone(UTC)
    millis = aware.microsecond // 1000
    return f"{aware.strftime('%Y-%m-%dT%H:%M:%S')}.{millis:03d}Z"


UtcDatetime = Annotated[
    datetime,
    AfterValidator(_ensure_utc),
    PlainSerializer(_serialize_utc, return_type=str, when_used="json"),
]

_STRICT = ConfigDict(extra="forbid")


class EventIdentity(BaseModel):
    model_config = _STRICT

    predicted_time_utc: UtcDatetime
    asteroid_number: int | None = Field(
        default=None, description="Minor-planet number; None for unnumbered objects"
    )
    asteroid_name: str
    provisional_designation: str | None = Field(
        default=None, description="Occult-XML compatibility, e.g. '2014 MU69'"
    )
    star_catalog: StarCatalog
    star_number: str = Field(
        description="Catalog-specific format, dashes preserved (e.g. '1234-56789-1')"
    )
    is_lucky_star_or_rio_tno: bool = False
    second_star: YesNoMaybe | None = None


class Observer(BaseModel):
    model_config = _STRICT

    names: list[str] = Field(min_length=1)
    email: EmailStr
    home_location: str = Field(description="City, State, Country (free text)")
    mailing_address: str | None = None
    phone: str | None = None


class Station(BaseModel):
    model_config = _STRICT

    location_name: str = Field(
        description="Nearest town + state/province + 2-letter country code"
    )
    latitude_deg: float = Field(
        ge=-90, le=90, description="Signed decimal degrees; South negative"
    )
    longitude_deg: float = Field(
        ge=-180, le=180, description="East positive, West negative"
    )
    elevation_m: float = Field(ge=-500, le=30000, description="Metres above MSL")
    datum: Datum = Datum.WGS84


class Telescope(BaseModel):
    model_config = _STRICT

    aperture_cm: float = Field(gt=0, le=25400)
    focal_ratio: float = Field(ge=0, le=999)
    magnification: float | None = Field(
        default=None, description="Visual observations only"
    )
    telescope_type: TelescopeType
    notes: str | None = Field(default=None, description="'other - specify' free text")


class TimingSetup(BaseModel):
    model_config = _STRICT

    time_source: TimeSource
    method: TimingMethod
    asteroid_visible: bool = Field(
        description="Asteroid visible before/during occultation (small mag-drop events)"
    )
    timing_device: TimingDevice = Field(description="The VTI (video time inserter)")
    ote_program: OteProgram = Field(
        description="Governs corrections; NONE == Excel's blank OTE"
    )


class RollingShutterInputs(BaseModel):
    model_config = _STRICT

    night_shutter: NightShutter
    star_y_at_d: int = Field(
        ge=0,
        le=575,
        description="Star Y-pixel at D (per-format max enforced by engine)",
    )
    star_y_at_r: int = Field(ge=0, le=575, description="Star Y-pixel at R")


class CameraSetup(BaseModel):
    model_config = _STRICT

    camera_model: CameraModel
    camera_other: str | None = Field(
        default=None, description="Required when camera_model == OTHER"
    )
    video_format: VideoFormat
    exposure: ExposureSetting = Field(description="Integration length in FIELDS")
    detector_notes: str | None = Field(
        default=None, description="Filter type / special settings"
    )
    rolling_shutter: RollingShutterInputs | None = Field(
        default=None,
        description="Required for RUNCAM_NIGHT_EAGLE_ASTRO in AUTO_CORRECTED mode",
    )


class ErrorBars(BaseModel):
    model_config = _STRICT

    cl_68: float | None = Field(default=None, ge=0, description="+/- s at 0.6827 CL")
    cl_95: float | None = Field(
        default=None, ge=0, description="+/- s at 0.9500 CL (primary accuracy)"
    )
    cl_9973: float | None = Field(default=None, ge=0, description="+/- s at 0.9973 CL")


class TimingMeasurement(BaseModel):
    model_config = _STRICT

    time_utc: UtcDatetime = Field(
        description="RAW time in AUTO_CORRECTED mode; FINAL time in MANUALLY_CORRECTED mode"
    )
    error_bars: ErrorBars = Field(default_factory=ErrorBars)
    personal_equation_s: float | None = Field(default=None, description="Visual only")
    personal_equation_applied: bool | None = None


class CorrectedTimings(BaseModel):
    """Computed correction block, embedded so the report is self-contained."""

    model_config = _STRICT

    disappearance_utc: UtcDatetime | None = None
    reappearance_utc: UtcDatetime | None = None
    camera_delay_d_s: float = 0.0
    camera_delay_r_s: float = 0.0
    vti_offset_d_s: float = 0.0
    vti_offset_r_s: float = 0.0
    total_correction_d_s: float = 0.0
    total_correction_r_s: float = 0.0
    near_midnight_review: bool = Field(
        default=False,
        description="Raw time within |correction| + 2s of 00:00:00 UT — review flag only",
    )


class EventTimings(BaseModel):
    model_config = _STRICT

    timing_mode: TimingMode
    start_observing_utc: UtcDatetime
    stop_observing_utc: UtcDatetime
    disappearance: TimingMeasurement | None = None
    reappearance: TimingMeasurement | None = None
    corrected: CorrectedTimings | None = Field(
        default=None,
        description="Populated by apply_corrections(); None until computed",
    )
    signal_to_noise: float | None = Field(default=None, ge=0)


class MissDetails(BaseModel):
    model_config = _STRICT

    was_miss: YesNoMaybe
    closest_approach_arcsec: float | None = None
    pass_direction: PassDirection | None = None


class ObservingInterruption(BaseModel):
    model_config = _STRICT

    start_utc: UtcDatetime
    end_utc: UtcDatetime
    reason: str | None = None


class Environment(BaseModel):
    model_config = _STRICT

    transparency: CloudCondition
    stability: Stability
    temperature_c: float | None = None
    other_conditions: str | None = None
    interruptions: list[ObservingInterruption] = Field(default_factory=list)


class Report(BaseModel):
    """A complete, portable occultation observation report."""

    model_config = _STRICT

    schema_version: str = SCHEMA_VERSION
    created_with: str | None = Field(
        default=None, description="Producing app + version, e.g. 'iota-hub/2026.07'"
    )
    result: ObservationResult
    event: EventIdentity
    observer: Observer
    station: Station
    telescope: Telescope
    timing_setup: TimingSetup
    camera: CameraSetup
    timings: EventTimings
    miss: MissDetails | None = None
    environment: Environment
    comments: str | None = None

    @model_validator(mode="after")
    def _validate_cross_fields(self) -> Report:
        # 1. Positive events require both D and R.
        if self.result == ObservationResult.POSITIVE and (
            self.timings.disappearance is None or self.timings.reappearance is None
        ):
            raise ValueError(
                "POSITIVE result requires both disappearance and reappearance timings"
            )

        # 2. RunCam Night Eagle Astro in auto mode requires rolling-shutter inputs.
        if (
            self.camera.camera_model == CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO
            and self.timings.timing_mode == TimingMode.AUTO_CORRECTED
            and self.camera.rolling_shutter is None
        ):
            raise ValueError(
                "RUNCAM_NIGHT_EAGLE_ASTRO in AUTO_CORRECTED mode requires "
                "camera.rolling_shutter (night shutter + star Y positions)"
            )

        # 3. camera_model == OTHER requires camera_other text.
        if (
            self.camera.camera_model == CameraModel.OTHER
            and not self.camera.camera_other
        ):
            raise ValueError("camera_model == OTHER requires camera.camera_other")

        # 4. stop must be after start.
        if self.timings.stop_observing_utc <= self.timings.start_observing_utc:
            raise ValueError("stop_observing_utc must be after start_observing_utc")

        # 5. Self-correcting cameras have no auto path.
        if (
            self.camera.camera_model in SELF_CORRECTING_CAMERAS
            and self.timings.timing_mode == TimingMode.AUTO_CORRECTED
        ):
            raise ValueError(
                f"camera_model {self.camera.camera_model.value} is self-correcting and "
                "must use MANUALLY_CORRECTED timing_mode"
            )

        return self
