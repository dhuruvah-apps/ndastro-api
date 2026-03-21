"""Unit tests for ndastro_api.services.transits."""

from ndastro_api.services.transits import (
    DEFAULT_ASPECTS,
    DEGREES_PER_RASI,
    DUSTHANA_HOUSES,
    FULL_CIRCLE_DEGREES,
    KENDRA_HOUSES,
    MARAKA_HOUSES,
    RASI_COUNT,
    TRIKONA_HOUSES,
    UPACHAYA_HOUSES,
    TransitHouseClass,
    TransitPlanetPosition,
    TransitSummary,
    build_house_transits,
    build_transit_positions,
    classify_transit_house,
    evaluate_transits,
    get_house_index,
    get_house_transit_interpretation,
    get_rasi_index,
    normalize_degrees,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_full_circle_degrees():
    assert FULL_CIRCLE_DEGREES == 360.0


def test_rasi_count():
    assert RASI_COUNT == 12


def test_degrees_per_rasi():
    assert DEGREES_PER_RASI == 30.0


def test_kendra_houses():
    assert {1, 4, 7, 10} == KENDRA_HOUSES


def test_trikona_houses():
    assert {1, 5, 9} == TRIKONA_HOUSES


def test_dusthana_houses():
    assert {6, 8, 12} == DUSTHANA_HOUSES


def test_upachaya_houses():
    assert {3, 6, 10, 11} == UPACHAYA_HOUSES


def test_maraka_houses():
    assert {2, 7} == MARAKA_HOUSES


def test_default_aspects_has_standard_planets():
    for planet in ("sun", "moon", "mars", "jupiter", "saturn"):
        assert planet in DEFAULT_ASPECTS


# ---------------------------------------------------------------------------
# TransitHouseClass enum
# ---------------------------------------------------------------------------


def test_transit_house_class_kendra_value():
    assert TransitHouseClass.KENDRA == "kendra"


def test_transit_house_class_dusthana_value():
    assert TransitHouseClass.DUSTHANA == "dusthana"


# ---------------------------------------------------------------------------
# normalize_degrees()
# ---------------------------------------------------------------------------


def test_normalize_degrees_positive():
    assert normalize_degrees(0.0) == 0.0


def test_normalize_degrees_over_360():
    assert abs(normalize_degrees(370.0) - 10.0) < 1e-6


def test_normalize_degrees_negative():
    assert abs(normalize_degrees(-10.0) - 350.0) < 1e-6


def test_normalize_degrees_exactly_360():
    assert normalize_degrees(360.0) == 0.0


# ---------------------------------------------------------------------------
# get_rasi_index()
# ---------------------------------------------------------------------------


def test_get_rasi_index_zero():
    assert get_rasi_index(0.0) == 1


def test_get_rasi_index_30():
    assert get_rasi_index(30.0) == 2


def test_get_rasi_index_359():
    assert get_rasi_index(359.9) == 12


def test_get_rasi_index_all_valid():
    for lon in range(0, 360, 5):
        idx = get_rasi_index(float(lon))
        assert 1 <= idx <= 12


# ---------------------------------------------------------------------------
# get_house_index()
# ---------------------------------------------------------------------------


def test_get_house_index_lagna():
    # planet at same longitude as lagna → house 1
    assert get_house_index(0.0, 0.0) == 1


def test_get_house_index_second_house():
    # planet 30° ahead of lagna → house 2
    assert get_house_index(30.0, 0.0) == 2


def test_get_house_index_in_range():
    for lon in range(0, 360, 30):
        h = get_house_index(float(lon), 0.0)
        assert 1 <= h <= 12


# ---------------------------------------------------------------------------
# classify_transit_house()
# ---------------------------------------------------------------------------


def test_classify_house_1_is_kendra():
    assert classify_transit_house(1) == TransitHouseClass.KENDRA


def test_classify_house_5_is_trikona():
    assert classify_transit_house(5) == TransitHouseClass.TRIKONA


def test_classify_house_9_is_trikona():
    assert classify_transit_house(9) == TransitHouseClass.TRIKONA


def test_classify_house_4_is_kendra():
    assert classify_transit_house(4) == TransitHouseClass.KENDRA


def test_classify_house_6_is_dusthana():
    assert classify_transit_house(6) == TransitHouseClass.DUSTHANA


def test_classify_house_8_is_dusthana():
    assert classify_transit_house(8) == TransitHouseClass.DUSTHANA


def test_classify_house_12_is_dusthana():
    assert classify_transit_house(12) == TransitHouseClass.DUSTHANA


def test_classify_house_3_is_upachaya():
    assert classify_transit_house(3) == TransitHouseClass.UPACHAYA


def test_classify_house_11_is_upachaya():
    assert classify_transit_house(11) == TransitHouseClass.UPACHAYA


def test_classify_house_2_is_maraka():
    assert classify_transit_house(2) == TransitHouseClass.MARAKA


def test_classify_house_7_is_kendra():
    # House 7 is in KENDRA_HOUSES and MARAKA_HOUSES; KENDRA is checked first
    assert classify_transit_house(7) == TransitHouseClass.KENDRA


# ---------------------------------------------------------------------------
# get_house_transit_interpretation()
# ---------------------------------------------------------------------------


def test_get_house_transit_interpretation_returns_str():
    result = get_house_transit_interpretation(1, ["jupiter"])
    assert isinstance(result, str) and len(result) > 0


def test_get_house_transit_interpretation_dusthana():
    result = get_house_transit_interpretation(8, ["saturn"])
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# build_transit_positions()
# ---------------------------------------------------------------------------


def test_build_transit_positions_returns_dict():
    positions = build_transit_positions({"sun": 15.0, "moon": 45.0}, 0.0)
    assert "sun" in positions
    assert "moon" in positions


def test_build_transit_positions_planet_is_dataclass():
    positions = build_transit_positions({"sun": 15.0}, 0.0)
    assert isinstance(positions["sun"], TransitPlanetPosition)


# ---------------------------------------------------------------------------
# build_house_transits()
# ---------------------------------------------------------------------------


def test_build_house_transits():
    positions = build_transit_positions({"sun": 0.0, "moon": 30.0}, 0.0)
    house_transits = build_house_transits(positions)
    assert isinstance(house_transits, dict)
    assert all(isinstance(v, list) for v in house_transits.values())


# ---------------------------------------------------------------------------
# evaluate_transits()
# ---------------------------------------------------------------------------


def test_evaluate_transits_returns_summary():
    transit_lons = {"sun": 15.0, "moon": 45.0}
    natal_lons = {"sun": 200.0, "moon": 100.0}
    result = evaluate_transits(transit_lons, natal_lons, 0.0)
    assert isinstance(result, TransitSummary)
    assert "sun" in result.positions
