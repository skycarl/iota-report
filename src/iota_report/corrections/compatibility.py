"""Camera x exposure x OTE compatibility checks.

Ports the Excel ``_CamExpArrayTable`` (excel-form-analysis §5.8/§6.4). The
spreadsheet *silently* withheld corrections for out-of-matrix combinations; here
we surface them as explicit, typed issues — the single most important behavioral
fix (design decision #14).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from iota_report.corrections.tables import (
    COMPATIBILITY_EXPOSURES,
    COMPATIBILITY_OTES,
)
from iota_report.enums import (
    LABELS,
    CameraModel,
    ExposureSetting,
    OteProgram,
    VideoFormat,
)


@dataclass(frozen=True)
class CompatibilityIssue:
    kind: Literal["exposure", "ote"]
    message: str


class CorrectionError(ValueError):
    """Base class for every timing-correction error.

    Subclasses :class:`ValueError` so existing ``except ValueError`` handlers keep
    working; callers wanting to catch the whole family should catch this class.
    """


class IncompatibleConfigurationError(CorrectionError):
    """Raised when a correction is requested for an out-of-matrix configuration."""

    def __init__(self, issues: list[CompatibilityIssue]):
        self.issues = issues
        super().__init__("; ".join(issue.message for issue in issues))


class InvalidCorrectionInputError(CorrectionError):
    """Raised when a correction input is individually invalid.

    Covers a rolling-shutter star-Y position outside the per-format range and
    missing rolling-shutter inputs for a camera that requires them. The model
    layer normally rejects these before they reach the engine; this guards direct
    engine callers who pass raw values.
    """


def check_compatibility(
    camera: CameraModel,
    exposure: ExposureSetting,
    ote: OteProgram,
    video_format: VideoFormat,  # noqa: ARG001 - reserved for future format checks; kept for API symmetry
) -> list[CompatibilityIssue]:
    """Return the compatibility issues for a configuration; empty list == valid."""
    issues: list[CompatibilityIssue] = []

    allowed_exposures = COMPATIBILITY_EXPOSURES.get(camera)
    if allowed_exposures is not None and exposure not in allowed_exposures:
        issues.append(
            CompatibilityIssue(
                kind="exposure",
                message=(
                    f"{LABELS[camera]} does not support {LABELS[exposure]} exposure"
                ),
            )
        )

    allowed_otes = COMPATIBILITY_OTES.get(camera)
    if allowed_otes is not None and ote not in allowed_otes:
        issues.append(
            CompatibilityIssue(
                kind="ote",
                message=(
                    f"{LABELS[camera]} is not compatible with the {LABELS[ote]} "
                    "timing-extraction program"
                ),
            )
        )

    return issues
