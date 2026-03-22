"""Divisional chart (varga) calculation utilities.

Provides a generic varga mapper plus common special-case rules.
Assumes longitudes are sidereal degrees in [0, 360).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ndastro_engine.utils import normalize_degree

FULL_CIRCLE_DEGREES = 360.0
RASI_COUNT = 12
DEGREES_PER_RASI = FULL_CIRCLE_DEGREES / RASI_COUNT
MOVABLE_SIGNS = {1, 4, 7, 10}
FIXED_SIGNS = {2, 5, 8, 11}
DUAL_SIGNS = {3, 6, 9, 12}

TRIMSAMSA_ODD_RANGES = [
    (5.0, 1),
    (10.0, 11),
    (18.0, 9),
    (25.0, 3),
    (30.0, 7),
]
TRIMSAMSA_EVEN_RANGES = [
    (5.0, 2),
    (12.0, 6),
    (20.0, 12),
    (25.0, 10),
    (30.0, 8),
]


class VargaType(str, Enum):
    """Known varga chart identifiers."""

    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"
    D7 = "D7"
    D9 = "D9"
    D10 = "D10"
    D12 = "D12"
    D16 = "D16"
    D20 = "D20"
    D24 = "D24"
    D27 = "D27"
    D30 = "D30"
    D40 = "D40"
    D45 = "D45"
    D60 = "D60"


@dataclass
class VargaPosition:
    """Represents a planet's varga placement."""

    planet: str
    longitude: float
    rasi: int
    varga_rasi: int
    division: int
    part_index: int


@dataclass
class VargaChart:
    """Computed varga chart for a set of planets."""

    varga: VargaType
    division: int
    positions: dict[str, VargaPosition] = field(default_factory=dict)


def _rasi_from_longitude(longitude: float) -> int:
    normalized = normalize_degree(longitude)
    return int(normalized / DEGREES_PER_RASI) + 1


def _degrees_in_rasi(longitude: float) -> float:
    normalized = normalize_degree(longitude)
    return normalized % DEGREES_PER_RASI


def _part_index(longitude: float, division: int) -> int:
    part_size = DEGREES_PER_RASI / division
    return int(_degrees_in_rasi(longitude) / part_size) + 1


def _wrap_rasi(rasi_index: int) -> int:
    return ((rasi_index - 1) % RASI_COUNT) + 1


def _is_odd_sign(rasi_index: int) -> bool:
    return rasi_index % 2 == 1


def _generic_varga_rasi(rasi_index: int, part_index: int, division: int) -> int:
    return _wrap_rasi((rasi_index - 1) * division + part_index)


def _hora_rasi(rasi_index: int, part_index: int) -> int:
    # Odd signs: Sun (Leo=5) then Moon (Cancer=4); even signs reversed.
    if _is_odd_sign(rasi_index):
        return 5 if part_index == 1 else 4
    return 4 if part_index == 1 else 5


def _drekkana_rasi(rasi_index: int, part_index: int) -> int:
    # Odd signs: 1st same, 2nd 5th, 3rd 9th; even signs reversed.
    offsets = [0, 4, 8] if _is_odd_sign(rasi_index) else [8, 4, 0]
    return _wrap_rasi(rasi_index + offsets[part_index - 1])


def _saptamsa_rasi(rasi_index: int, part_index: int) -> int:
    # Odd signs start from sign itself; even signs start from 7th.
    start = rasi_index if _is_odd_sign(rasi_index) else _wrap_rasi(rasi_index + 6)
    return _wrap_rasi(start + part_index - 1)


def _navamsa_rasi(rasi_index: int, part_index: int) -> int:
    # Standard Navamsa: movable start Aries, fixed start Capricorn, dual start Libra.
    if rasi_index in MOVABLE_SIGNS:
        start = 1
    elif rasi_index in FIXED_SIGNS:
        start = 10
    else:
        start = 7

    return _wrap_rasi(start + part_index - 1)


def _dasamsa_rasi(rasi_index: int, part_index: int) -> int:
    # Odd signs start from sign itself; even signs start from 9th from sign.
    start = rasi_index if _is_odd_sign(rasi_index) else _wrap_rasi(rasi_index + 8)
    return _wrap_rasi(start + part_index - 1)


def _dwadasamsa_rasi(rasi_index: int, part_index: int) -> int:
    # D12: starts from the sign itself and cycles through.
    return _wrap_rasi(rasi_index + part_index - 1)


def _shodasamsa_rasi(rasi_index: int, part_index: int) -> int:
    # D16: movable start Aries, fixed start Leo, dual start Sagittarius.
    if rasi_index in MOVABLE_SIGNS:
        start = 1
    elif rasi_index in FIXED_SIGNS:
        start = 5
    else:
        start = 9

    return _wrap_rasi(start + part_index - 1)


def _vimsamsa_rasi(rasi_index: int, part_index: int) -> int:
    # D20: movable start Aries, fixed start Sagittarius, dual start Leo.
    if rasi_index in MOVABLE_SIGNS:
        start = 1
    elif rasi_index in FIXED_SIGNS:
        start = 9
    else:
        start = 5

    return _wrap_rasi(start + part_index - 1)


def _chaturvimsamsa_rasi(rasi_index: int, part_index: int) -> int:
    # D24: odd signs start Leo, even signs start Cancer.
    start = 5 if _is_odd_sign(rasi_index) else 4
    return _wrap_rasi(start + part_index - 1)


def _trimsamsa_rasi(longitude: float, rasi_index: int) -> int:
    # D30: unequal divisions by sign parity.
    degree_in_sign = _degrees_in_rasi(longitude)
    ranges = TRIMSAMSA_ODD_RANGES if _is_odd_sign(rasi_index) else TRIMSAMSA_EVEN_RANGES

    for max_degree, rasi in ranges:
        if degree_in_sign < max_degree:
            return rasi

    return ranges[-1][1]


def _khavedamsa_rasi(rasi_index: int, part_index: int) -> int:
    # D40: odd signs start Aries, even signs start Libra.
    start = 1 if _is_odd_sign(rasi_index) else 7
    return _wrap_rasi(start + part_index - 1)


def _akshavedamsa_rasi(rasi_index: int, part_index: int) -> int:
    # D45: movable start Aries, fixed start Leo, dual start Sagittarius.
    if rasi_index in MOVABLE_SIGNS:
        start = 1
    elif rasi_index in FIXED_SIGNS:
        start = 5
    else:
        start = 9

    return _wrap_rasi(start + part_index - 1)


def _shashtiamsa_rasi(rasi_index: int, part_index: int) -> int:
    # D60: odd signs start Aries, even signs start Libra.
    start = 1 if _is_odd_sign(rasi_index) else 7
    return _wrap_rasi(start + part_index - 1)


def get_varga_rasi(longitude: float, division: int) -> int:
    """Return varga rasi index for a longitude using generic formula."""
    rasi_index = _rasi_from_longitude(longitude)
    part = _part_index(longitude, division)
    return _generic_varga_rasi(rasi_index, part, division)


def get_varga_rasi_with_rules(longitude: float, varga: VargaType) -> int:
    """Return varga rasi index using common classical rules."""
    rasi_index = _rasi_from_longitude(longitude)
    division = int(varga.value[1:])
    part = _part_index(longitude, division)

    rule_map = {
        VargaType.D2: lambda: _hora_rasi(rasi_index, part),
        VargaType.D3: lambda: _drekkana_rasi(rasi_index, part),
        VargaType.D7: lambda: _saptamsa_rasi(rasi_index, part),
        VargaType.D9: lambda: _navamsa_rasi(rasi_index, part),
        VargaType.D10: lambda: _dasamsa_rasi(rasi_index, part),
        VargaType.D12: lambda: _dwadasamsa_rasi(rasi_index, part),
        VargaType.D16: lambda: _shodasamsa_rasi(rasi_index, part),
        VargaType.D20: lambda: _vimsamsa_rasi(rasi_index, part),
        VargaType.D24: lambda: _chaturvimsamsa_rasi(rasi_index, part),
        VargaType.D30: lambda: _trimsamsa_rasi(longitude, rasi_index),
        VargaType.D40: lambda: _khavedamsa_rasi(rasi_index, part),
        VargaType.D45: lambda: _akshavedamsa_rasi(rasi_index, part),
        VargaType.D60: lambda: _shashtiamsa_rasi(rasi_index, part),
    }

    handler = rule_map.get(varga)
    if handler:
        return handler()

    return _generic_varga_rasi(rasi_index, part, division)


def compute_varga_chart(
    longitudes: dict[str, float],
    varga: VargaType,
) -> VargaChart:
    """Compute a varga chart for a set of longitudes."""
    division = int(varga.value[1:])
    chart = VargaChart(varga=varga, division=division)

    for planet, longitude in longitudes.items():
        rasi_index = _rasi_from_longitude(longitude)
        part = _part_index(longitude, division)
        varga_rasi = get_varga_rasi_with_rules(longitude, varga)

        chart.positions[planet] = VargaPosition(
            planet=planet,
            longitude=normalize_degree(longitude),
            rasi=rasi_index,
            varga_rasi=varga_rasi,
            division=division,
            part_index=part,
        )

    return chart
