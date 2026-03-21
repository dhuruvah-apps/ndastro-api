"""Unit tests for ndastro_api.services.divisional_charts."""

import pytest

from ndastro_api.services.divisional_charts import (
    DUAL_SIGNS,
    FIXED_SIGNS,
    MOVABLE_SIGNS,
    VargaChart,
    VargaPosition,
    VargaType,
    _degrees_in_rasi,
    _hora_rasi,
    _is_odd_sign,
    _navamsa_rasi,
    _normalize_degrees,
    _rasi_from_longitude,
    _wrap_rasi,
)

# ---------------------------------------------------------------------------
# Sign classification sets
# ---------------------------------------------------------------------------


def test_movable_fixed_dual_cover_all_12():
    all_signs = MOVABLE_SIGNS | FIXED_SIGNS | DUAL_SIGNS
    assert all_signs == set(range(1, 13))


def test_sign_sets_are_disjoint():
    assert not (MOVABLE_SIGNS & FIXED_SIGNS)
    assert not (MOVABLE_SIGNS & DUAL_SIGNS)
    assert not (FIXED_SIGNS & DUAL_SIGNS)


# ---------------------------------------------------------------------------
# _normalize_degrees()
# ---------------------------------------------------------------------------


def test_normalize_degrees_zero():
    assert _normalize_degrees(0.0) == pytest.approx(0.0)


def test_normalize_degrees_positive():
    assert _normalize_degrees(270.0) == pytest.approx(270.0)


def test_normalize_degrees_over_360():
    assert _normalize_degrees(370.0) == pytest.approx(10.0)


def test_normalize_degrees_negative():
    assert _normalize_degrees(-10.0) == pytest.approx(350.0)


# ---------------------------------------------------------------------------
# _rasi_from_longitude()
# ---------------------------------------------------------------------------


def test_rasi_from_longitude_0():
    assert _rasi_from_longitude(0.0) == 1  # 0–30° → Rasi 1


def test_rasi_from_longitude_30():
    assert _rasi_from_longitude(30.0) == 2


def test_rasi_from_longitude_359():
    assert _rasi_from_longitude(359.9) == 12


# ---------------------------------------------------------------------------
# _degrees_in_rasi()
# ---------------------------------------------------------------------------


def test_degrees_in_rasi_at_45():
    assert _degrees_in_rasi(45.0) == pytest.approx(15.0)  # 45 − 30 = 15


def test_degrees_in_rasi_at_0():
    assert _degrees_in_rasi(0.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# _wrap_rasi()
# ---------------------------------------------------------------------------


def test_wrap_rasi_12():
    assert _wrap_rasi(12) == 12


def test_wrap_rasi_13_wraps_to_1():
    assert _wrap_rasi(13) == 1


def test_wrap_rasi_0_wraps_to_12():
    assert _wrap_rasi(0) == 12


# ---------------------------------------------------------------------------
# _is_odd_sign()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rasi,expected", [(1, True), (2, False), (11, True), (12, False)])
def test_is_odd_sign(rasi, expected):
    assert _is_odd_sign(rasi) == expected


# ---------------------------------------------------------------------------
# _hora_rasi()
# ---------------------------------------------------------------------------


def test_hora_rasi_odd_sign_part1():
    """Odd sign, part 1 → Sun (Leo = 5)."""
    assert _hora_rasi(1, 1) == 5


def test_hora_rasi_odd_sign_part2():
    """Odd sign, part 2 → Moon (Cancer = 4)."""
    assert _hora_rasi(1, 2) == 4


def test_hora_rasi_even_sign_part1():
    """Even sign, part 1 → Moon (Cancer = 4)."""
    assert _hora_rasi(2, 1) == 4


# ---------------------------------------------------------------------------
# _navamsa_rasi()
# ---------------------------------------------------------------------------


def test_navamsa_rasi_movable_sign_part1():
    """Movable sign (1), part 1 → starts at Aries (1)."""
    assert _navamsa_rasi(1, 1) == 1


def test_navamsa_rasi_fixed_sign_part1():
    """Fixed sign (2), part 1 → starts at Capricorn (10)."""
    assert _navamsa_rasi(2, 1) == 10


def test_navamsa_rasi_dual_sign_part1():
    """Dual sign (3), part 1 → starts at Libra (7)."""
    assert _navamsa_rasi(3, 1) == 7


def test_navamsa_rasi_result_in_range():
    for rasi in range(1, 13):
        for part in range(1, 10):
            result = _navamsa_rasi(rasi, part)
            assert 1 <= result <= 12


# ---------------------------------------------------------------------------
# VargaType enum
# ---------------------------------------------------------------------------


def test_varga_type_values():
    assert VargaType.D9 == "D9"
    assert VargaType.D1 == "D1"
    assert VargaType.D60 == "D60"


# ---------------------------------------------------------------------------
# VargaPosition dataclass
# ---------------------------------------------------------------------------


def test_varga_position_construction():
    pos = VargaPosition(planet="SU", longitude=45.0, rasi=2, varga_rasi=6, division=9, part_index=2)
    assert pos.planet == "SU"
    assert pos.rasi == 2


# ---------------------------------------------------------------------------
# VargaChart dataclass
# ---------------------------------------------------------------------------


def test_varga_chart_default_positions_empty():
    chart = VargaChart(varga=VargaType.D9, division=9)
    assert chart.positions == {}


def test_varga_chart_holds_positions():
    pos = VargaPosition(planet="MO", longitude=90.0, rasi=4, varga_rasi=8, division=9, part_index=3)
    chart = VargaChart(varga=VargaType.D9, division=9, positions={"MO": pos})
    assert "MO" in chart.positions
