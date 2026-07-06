"""Legacy coordinate-string parsing helpers.

The report model stores signed decimal degrees. Observers historically entered
latitude/longitude in one of three interchangeable display formats (Excel form,
excel-form-analysis §2.3):

- ``deg mm sec.ss``  (space-separated degrees, minutes, seconds) — OCCULT default
- ``deg min.mmm``    (degrees + decimal minutes)
- ``deg.ddddd``      (decimal degrees)

Hemisphere is a separate ``N/S`` or ``E/W`` field; ``S`` and ``W`` are negative
(matching the text form's "East +ve / South -ve" convention).
"""

from __future__ import annotations

_SOUTH_WEST = {"S", "W"}
_NORTH_EAST = {"N", "E"}
_VALID_HEMISPHERES = _SOUTH_WEST | _NORTH_EAST


def parse_coordinate(value: str, hemisphere: str | None = None) -> float:
    """Parse a legacy coordinate string into signed decimal degrees.

    The format is auto-detected by token count:
    one token → decimal degrees, two → degrees + decimal minutes,
    three → degrees minutes seconds.

    ``hemisphere`` is one of ``N``/``S``/``E``/``W`` (case-insensitive) or None.
    ``S``/``W`` negate the magnitude. A leading sign on ``value`` is honored only
    when ``hemisphere`` is None; supplying both a negative value and an ``S``/``W``
    hemisphere raises ``ValueError`` (ambiguous double-negation).
    """
    if value is None:
        raise ValueError("coordinate value is required")

    raw = value.strip()
    if not raw:
        raise ValueError("coordinate value is empty")

    hemi = hemisphere.strip().upper() if hemisphere else None
    if hemi is not None and hemi not in _VALID_HEMISPHERES:
        raise ValueError(f"invalid hemisphere: {hemisphere!r} (expected N/S/E/W)")

    negative_value = raw.startswith("-")
    tokens = raw.lstrip("+-").split()
    if not tokens:
        raise ValueError(f"could not parse coordinate: {value!r}")

    try:
        numbers = [float(tok) for tok in tokens]
    except ValueError as exc:
        raise ValueError(f"non-numeric token in coordinate: {value!r}") from exc

    if any(n < 0 for n in numbers):
        raise ValueError(f"minutes/seconds components must be non-negative: {value!r}")

    if len(numbers) == 1:
        magnitude = numbers[0]
    elif len(numbers) == 2:
        deg, minutes = numbers
        if minutes >= 60:
            raise ValueError(f"minutes must be < 60: {value!r}")
        magnitude = deg + minutes / 60.0
    elif len(numbers) == 3:
        deg, minutes, seconds = numbers
        if minutes >= 60:
            raise ValueError(f"minutes must be < 60: {value!r}")
        if seconds >= 60:
            raise ValueError(f"seconds must be < 60: {value!r}")
        magnitude = deg + minutes / 60.0 + seconds / 3600.0
    else:
        raise ValueError(
            f"expected 1-3 whitespace-separated tokens, got {len(numbers)}: {value!r}"
        )

    if hemi in _SOUTH_WEST:
        if negative_value:
            raise ValueError(
                "ambiguous sign: value is negative and hemisphere is "
                f"{hemi!r}; provide only one"
            )
        return -magnitude
    if hemi in _NORTH_EAST:
        return magnitude

    # No hemisphere: honor the sign on the value.
    return -magnitude if negative_value else magnitude


def parse_latitude(value: str, hemisphere: str | None = None) -> float:
    """Parse a latitude string to signed decimal degrees, range-checked to +/-90."""
    result = parse_coordinate(value, hemisphere)
    if not -90.0 <= result <= 90.0:
        raise ValueError(f"latitude out of range [-90, 90]: {result}")
    return result


def parse_longitude(value: str, hemisphere: str | None = None) -> float:
    """Parse a longitude string to signed decimal degrees, range-checked to +/-180."""
    result = parse_coordinate(value, hemisphere)
    if not -180.0 <= result <= 180.0:
        raise ValueError(f"longitude out of range [-180, 180]: {result}")
    return result
