"""Unit tests for ndastro_api.services.upagrahas."""

from ndastro_api.services.upagrahas import (
    DHUMA_OFFSET,
    DIVISION_PARTS,
    FULL_CIRCLE,
    INDRACHAAPA_OFFSET,
    PARIVESHA_OFFSET,
    RASI_COUNT,
    UPAKETU_OFFSET,
    VYATIPAATA_OFFSET,
    PlanetRuler,
    Upagraha,
    UpagrahaType,
    calculate_sun_based_upagrahas,
    get_all_sun_based_upagrahas,
    get_upagraha_interpretation,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_full_circle():
    assert FULL_CIRCLE == 360.0


def test_rasi_count():
    assert RASI_COUNT == 12


def test_division_parts():
    assert DIVISION_PARTS == 8


def test_dhuma_offset():
    expected = 133 + 20 / 60
    assert abs(DHUMA_OFFSET - expected) < 1e-6


def test_upaketu_offset():
    expected = 16 + 40 / 60
    assert abs(UPAKETU_OFFSET - expected) < 1e-6


def test_vyatipaata_offset():
    assert VYATIPAATA_OFFSET == 360.0


def test_parivesha_offset():
    assert PARIVESHA_OFFSET == 180.0


def test_indrachaapa_offset():
    assert INDRACHAAPA_OFFSET == 360.0


# ---------------------------------------------------------------------------
# UpagrahaType enum
# ---------------------------------------------------------------------------


def test_upagraha_type_dhuma():
    assert UpagrahaType.DHUMA == "dhuma"


def test_upagraha_type_gulika():
    assert UpagrahaType.GULIKA == "gulika"


def test_upagraha_type_maandi():
    assert UpagrahaType.MAANDI == "maandi"


def test_upagraha_type_has_11_members():
    assert len(list(UpagrahaType)) == 11


# ---------------------------------------------------------------------------
# PlanetRuler enum
# ---------------------------------------------------------------------------


def test_planet_ruler_sun():
    assert PlanetRuler.SUN == "sun"


def test_planet_ruler_lordless():
    assert PlanetRuler.LORDLESS == "lordless"


# ---------------------------------------------------------------------------
# calculate_sun_based_upagrahas()
# ---------------------------------------------------------------------------


def test_calculate_sun_based_returns_dict():
    result = calculate_sun_based_upagrahas(0.0)
    assert isinstance(result, dict)


def test_calculate_sun_based_has_5_entries():
    result = calculate_sun_based_upagrahas(0.0)
    assert len(result) == 5


def test_calculate_sun_based_keys_are_upagraha_types():
    result = calculate_sun_based_upagrahas(0.0)
    sun_based = {UpagrahaType.DHUMA, UpagrahaType.VYATIPAATA, UpagrahaType.PARIVESHA, UpagrahaType.INDRACHAAPA, UpagrahaType.UPAKETU}
    assert set(result.keys()) == sun_based


def test_calculate_sun_based_values_in_range():
    result = calculate_sun_based_upagrahas(45.0)
    for lon in result.values():
        assert 0.0 <= lon < 360.0


def test_calculate_sun_based_varies_with_sun():
    r1 = calculate_sun_based_upagrahas(0.0)
    r2 = calculate_sun_based_upagrahas(90.0)
    # At least one upagraha should differ
    assert any(r1[k] != r2[k] for k in r1)


# ---------------------------------------------------------------------------
# get_all_sun_based_upagrahas()
# ---------------------------------------------------------------------------


def test_get_all_sun_based_returns_list():
    result = get_all_sun_based_upagrahas(0.0)
    assert isinstance(result, list)


def test_get_all_sun_based_has_5_entries():
    result = get_all_sun_based_upagrahas(0.0)
    assert len(result) == 5


def test_get_all_sun_based_items_are_upagraha():
    result = get_all_sun_based_upagrahas(0.0)
    for item in result:
        assert isinstance(item, Upagraha)


def test_get_all_sun_based_rasi_number_in_range():
    result = get_all_sun_based_upagrahas(45.0)
    for item in result:
        assert 1 <= item.rasi_number <= 12


# ---------------------------------------------------------------------------
# get_upagraha_interpretation()
# ---------------------------------------------------------------------------


def test_get_upagraha_interpretation_returns_str():
    upagrahas = get_all_sun_based_upagrahas(0.0)
    result = get_upagraha_interpretation(upagrahas[0])
    assert isinstance(result, str) and len(result) > 0
