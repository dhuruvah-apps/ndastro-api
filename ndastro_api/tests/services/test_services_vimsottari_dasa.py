"""Unit tests for ndastro_api.services.vimsottari_dasa."""

import pytest

from ndastro_api.services.vimsottari_dasa import (
    DASA_SEQUENCE,
    DASA_YEARS,
    NAKSHATRA_RULERS,
    TOTAL_DASA_YEARS,
    DasaLevel,
    calculate_dasa_start_planet_and_fraction,
    get_nakshatra_ruler,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_dasa_years_total_matches_constant():
    """The DASA_YEARS entries should sum to the module-level TOTAL_DASA_YEARS constant."""
    assert sum(DASA_YEARS.values()) == TOTAL_DASA_YEARS


def test_dasa_sequence_has_9_planets():
    assert len(DASA_SEQUENCE) == 9


def test_nakshatra_rulers_covers_1_to_27():
    # should have entries for all 27 nakshatras
    for i in range(1, 28):
        assert i in NAKSHATRA_RULERS, f"Nakshatra {i} missing from NAKSHATRA_RULERS"


def test_all_nakshatra_rulers_value_in_dasa_years():
    for nak, ruler in NAKSHATRA_RULERS.items():
        assert ruler in DASA_YEARS, f"Nakshatra {nak} ruler '{ruler}' not in DASA_YEARS"


# ---------------------------------------------------------------------------
# DasaLevel enum
# ---------------------------------------------------------------------------


def test_dasa_level_values():
    assert DasaLevel.MAHA == "maha"
    assert DasaLevel.BHUKTI == "bhukti"
    assert DasaLevel.ANTARA == "antara"
    assert DasaLevel.PRATYANTARA == "pratyantara"


# ---------------------------------------------------------------------------
# get_nakshatra_ruler()
# ---------------------------------------------------------------------------


def test_get_nakshatra_ruler_ashwini():
    """Nakshatra 1 (Ashwini) is ruled by Kethu."""
    assert get_nakshatra_ruler(1) == "kethu"


def test_get_nakshatra_ruler_rohini():
    """Nakshatra 4 (Rohini) is ruled by Moon."""
    assert get_nakshatra_ruler(4) == "moon"


def test_get_nakshatra_ruler_out_of_range_low():
    """Values below 1 clamp to 1."""
    assert get_nakshatra_ruler(0) == get_nakshatra_ruler(1)


def test_get_nakshatra_ruler_out_of_range_high():
    """Values above 27 clamp to 27."""
    assert get_nakshatra_ruler(28) == get_nakshatra_ruler(27)


# ---------------------------------------------------------------------------
# calculate_dasa_start_planet_and_fraction()
# ---------------------------------------------------------------------------


def test_dasa_start_fraction_at_pada_0():
    planet, fraction = calculate_dasa_start_planet_and_fraction(1, 0.0)
    assert planet == "kethu"
    assert fraction == pytest.approx(0.0)


def test_dasa_start_fraction_at_pada_4():
    """Full nakshatra traversal → fraction = planet_years / total_years."""
    planet, fraction = calculate_dasa_start_planet_and_fraction(1, 4.0)
    expected = 1.0 * (DASA_YEARS["kethu"] / TOTAL_DASA_YEARS)
    assert fraction == pytest.approx(expected)


def test_dasa_start_planet_matches_nakshatra_ruler():
    for nak in range(1, 28):
        ruler = get_nakshatra_ruler(nak)
        planet, _ = calculate_dasa_start_planet_and_fraction(nak, 0.0)
        assert planet == ruler, f"Nakshatra {nak}: expected {ruler}, got {planet}"
