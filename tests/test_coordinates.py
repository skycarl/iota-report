"""Coordinate-parsing tests: 3 legacy formats x both hemispheres + sign conflict."""

from __future__ import annotations

import pytest

from iota_report import parse_coordinate, parse_latitude, parse_longitude


@pytest.mark.parametrize(
    "value,hemisphere,expected",
    [
        # deg mm sec.ss
        ("37 30 00.00", "N", 37.5),
        ("37 30 00.00", "S", -37.5),
        # deg min.mmm
        ("37 30.000", "N", 37.5),
        ("37 30.000", "S", -37.5),
        # deg.ddddd
        ("37.5", "N", 37.5),
        ("37.5", "S", -37.5),
        # longitude east/west
        ("77 24 00.00", "E", 77.4),
        ("77 24 00.00", "W", -77.4),
        ("122 30.000", "E", 122.5),
        ("122 30.000", "W", -122.5),
    ],
)
def test_parse_coordinate_all_formats(
    value: str, hemisphere: str, expected: float
) -> None:
    assert parse_coordinate(value, hemisphere) == pytest.approx(expected, abs=1e-9)


def test_leading_sign_honored_without_hemisphere() -> None:
    assert parse_coordinate("-37.5") == pytest.approx(-37.5)
    assert parse_coordinate("37.5") == pytest.approx(37.5)


def test_sign_conflict_raises() -> None:
    with pytest.raises(ValueError, match="ambiguous sign"):
        parse_coordinate("-37.5", "S")


def test_invalid_hemisphere_raises() -> None:
    with pytest.raises(ValueError, match="invalid hemisphere"):
        parse_coordinate("37.5", "X")


def test_minutes_and_seconds_bounds() -> None:
    with pytest.raises(ValueError, match="minutes must be"):
        parse_coordinate("37 60 00", "N")
    with pytest.raises(ValueError, match="seconds must be"):
        parse_coordinate("37 30 60", "N")


def test_empty_value_raises() -> None:
    with pytest.raises(ValueError):
        parse_coordinate("   ", "N")


def test_latitude_range_check() -> None:
    assert parse_latitude("89 59 59.9", "N") == pytest.approx(89.99997222, abs=1e-6)
    with pytest.raises(ValueError, match="latitude out of range"):
        parse_latitude("91 00 00", "N")


def test_longitude_range_check() -> None:
    assert parse_longitude("179 30.000", "E") == pytest.approx(179.5)
    with pytest.raises(ValueError, match="longitude out of range"):
        parse_longitude("181 00 00", "E")
