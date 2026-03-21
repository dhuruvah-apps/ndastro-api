"""Unit tests for ndastro_api.services.longevity."""

from ndastro_api.services.longevity import (
    BENEFIC_PLANETS,
    HOUSE_1_SELF,
    HOUSE_8_LONGEVITY,
    HOUSE_12_LOSS,
    MALEFIC_PLANETS,
    RASI_ARIES,
    RASI_LORDS,
    RASI_PISCES,
    TOTAL_RASIS,
    HouseCategory,
    LongevityCategory,
    MarakaType,
    RasiType,
    categorize_house_position,
    get_house_from_rasi,
    get_rasi_at_house,
    get_rasi_lord,
    get_rasi_type,
    get_trine_rasis,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_total_rasis():
    assert TOTAL_RASIS == 12


def test_house_1():
    assert HOUSE_1_SELF == 1


def test_house_8():
    assert HOUSE_8_LONGEVITY == 8


def test_house_12():
    assert HOUSE_12_LOSS == 12


def test_rasi_aries():
    assert RASI_ARIES == 1


def test_rasi_pisces():
    assert RASI_PISCES == 12


def test_rasi_lords_has_12_entries():
    assert len(RASI_LORDS) == 12


def test_benefic_planets_nonempty():
    assert len(BENEFIC_PLANETS) > 0
    assert "jupiter" in BENEFIC_PLANETS


def test_malefic_planets_nonempty():
    assert len(MALEFIC_PLANETS) > 0
    assert "saturn" in MALEFIC_PLANETS


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


def test_longevity_category_short():
    assert LongevityCategory.SHORT_LIFE == "short_life"


def test_longevity_category_long():
    assert LongevityCategory.LONG_LIFE == "long_life"


def test_rasi_type_movable():
    assert RasiType.MOVABLE == "movable"


def test_rasi_type_fixed():
    assert RasiType.FIXED == "fixed"


def test_rasi_type_dual():
    assert RasiType.DUAL == "dual"


def test_house_category_quadrant():
    assert HouseCategory.QUADRANT == "quadrant"


def test_maraka_type_has_members():
    assert len(list(MarakaType)) > 0


# ---------------------------------------------------------------------------
# get_rasi_type()
# ---------------------------------------------------------------------------


def test_aries_is_movable():
    assert get_rasi_type(1) == RasiType.MOVABLE


def test_taurus_is_fixed():
    assert get_rasi_type(2) == RasiType.FIXED


def test_gemini_is_dual():
    assert get_rasi_type(3) == RasiType.DUAL


def test_cancer_is_movable():
    assert get_rasi_type(4) == RasiType.MOVABLE


def test_leo_is_fixed():
    assert get_rasi_type(5) == RasiType.FIXED


def test_pisces_is_dual():
    assert get_rasi_type(12) == RasiType.DUAL


# ---------------------------------------------------------------------------
# get_rasi_lord()
# ---------------------------------------------------------------------------


def test_aries_lord_is_mars():
    assert get_rasi_lord(1) == "mars"


def test_taurus_lord_is_venus():
    assert get_rasi_lord(2) == "venus"


def test_gemini_lord_is_mercury():
    assert get_rasi_lord(3) == "mercury"


def test_cancer_lord_is_moon():
    assert get_rasi_lord(4) == "moon"


def test_leo_lord_is_sun():
    assert get_rasi_lord(5) == "sun"


def test_sagittarius_lord_is_jupiter():
    assert get_rasi_lord(9) == "jupiter"


def test_capricorn_lord_is_saturn():
    assert get_rasi_lord(10) == "saturn"


# ---------------------------------------------------------------------------
# get_house_from_rasi()
# ---------------------------------------------------------------------------


def test_house_from_rasi_same():
    # lagna_rasi == target_rasi → house 1
    assert get_house_from_rasi(1, 1) == 1


def test_house_from_rasi_fourth():
    # lagna rasi 1, target rasi 4 → house 4
    assert get_house_from_rasi(1, 4) == 4


def test_house_from_rasi_wrap():
    # lagna rasi 12, target rasi 1 → house 2
    assert get_house_from_rasi(12, 1) == 2


def test_house_from_rasi_seventh():
    assert get_house_from_rasi(1, 7) == 7


# ---------------------------------------------------------------------------
# get_rasi_at_house()
# ---------------------------------------------------------------------------


def test_rasi_at_house_1():
    assert get_rasi_at_house(1, 1) == 1


def test_rasi_at_house_2():
    assert get_rasi_at_house(1, 2) == 2


def test_rasi_at_house_wrap():
    # lagna rasi 11, house 3 → rasi 13 → wraps to 1
    assert get_rasi_at_house(11, 3) == 1


# ---------------------------------------------------------------------------
# get_trine_rasis()
# ---------------------------------------------------------------------------


def test_trine_rasis_aries():
    trines = get_trine_rasis(1)
    assert sorted(trines) == [1, 5, 9]


def test_trine_rasis_cancer():
    trines = get_trine_rasis(4)
    assert sorted(trines) == [4, 8, 12]


def test_trine_rasis_returns_3():
    assert len(get_trine_rasis(7)) == 3


# ---------------------------------------------------------------------------
# categorize_house_position()
# ---------------------------------------------------------------------------


def test_house_1_is_quadrant():
    assert categorize_house_position(1) == HouseCategory.QUADRANT


def test_house_4_is_quadrant():
    assert categorize_house_position(4) == HouseCategory.QUADRANT


def test_house_7_is_quadrant():
    assert categorize_house_position(7) == HouseCategory.QUADRANT


def test_house_10_is_quadrant():
    assert categorize_house_position(10) == HouseCategory.QUADRANT


def test_house_2_is_panaphara():
    assert categorize_house_position(2) == HouseCategory.PANAPHARA


def test_house_5_is_panaphara():
    assert categorize_house_position(5) == HouseCategory.PANAPHARA


def test_house_3_is_apoklima():
    assert categorize_house_position(3) == HouseCategory.APOKLIMA


def test_house_6_is_apoklima():
    assert categorize_house_position(6) == HouseCategory.APOKLIMA
