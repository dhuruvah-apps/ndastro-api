"""Unit tests for ndastro_api.core.constants."""
from ndastro_api.core.constants import (
    AYANAMSA,
    KATTAM_RASI_MAP,
    SYMBOLS
)

from ndastro_engine.constants import DEGREE_MAX, DEGREE_PER_RASI, TOTAL_RASI, TOTAL_NAKSHATRAS, TOTAL_PADA, DEGREE_PER_NAKSHATRA, DEGREE_PER_PADA, HALF_CIRCLE_DEGREES

# ---------------------------------------------------------------------------
# Numeric constants
# ---------------------------------------------------------------------------


def test_degree_max():
    assert DEGREE_MAX == 360


def test_half_circle():
    assert HALF_CIRCLE_DEGREES == 180.0


def test_degrees_per_raasi():
    assert DEGREE_PER_RASI == 30


def test_total_raasi():
    assert TOTAL_RASI == 12


def test_total_nakshatras():
    assert TOTAL_NAKSHATRAS == 27


def test_total_pada():
    assert TOTAL_PADA == 4


def test_degrees_per_nakshatra():
    """360 / 27 ≈ 13.333°."""
    import pytest

    assert pytest.approx(360 / 27) == DEGREE_PER_NAKSHATRA


def test_degrees_per_pada():
    """360 / (27*4) ≈ 3.333°."""
    import pytest

    assert pytest.approx(360 / 108) == DEGREE_PER_PADA


def test_kattam_rasi_map_length():
    assert len(KATTAM_RASI_MAP) == 12


def test_kattam_rasi_map_contains_all_rasis():
    assert sorted(KATTAM_RASI_MAP) == list(range(1, 13))


# ---------------------------------------------------------------------------
# SYMBOLS class
# ---------------------------------------------------------------------------


def test_symbols_degree():
    assert SYMBOLS.DEGREE_SYMBOL == "°"


def test_symbols_retrograde():
    assert SYMBOLS.RETROGRADE_SYMBOL == "℞"


def test_symbols_ascendant():
    assert SYMBOLS.ASENDENT_SYMBOL == "L"


# ---------------------------------------------------------------------------
# AYANAMSA class constants
# ---------------------------------------------------------------------------


def test_ayanamsa_century_constants():
    assert AYANAMSA.CENTURY_19 == 1900
    assert AYANAMSA.CENTURY_20 == 2000
    assert AYANAMSA.CENTURY_21 == 2100


def test_ayanamsa_lahiri_value():
    assert AYANAMSA.LAHIRI == 24.12


def test_ayanamsa_instance_name():
    a = AYANAMSA("lahiri")
    assert a.name == "lahiri"


def test_ayanamsa_instance_value_lahiri():
    a = AYANAMSA("lahiri")
    assert a.value == AYANAMSA.LAHIRI


def test_ayanamsa_instance_value_unknown_defaults_to_lahiri():
    a = AYANAMSA("unknown")
    assert a.value == AYANAMSA.LAHIRI
