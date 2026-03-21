"""Unit tests for ndastro_api.services.ashtakavarga."""

from ndastro_api.services.ashtakavarga import (
    BENEFIC_PLANETS,
    HOUSES_PER_PLANET,
    MALEFIC_PLANETS,
    MAX_AVG_POINTS,
    MODERATE_HOUSE_THRESHOLD,
    PLANET_HOUSES,
    RASI_COUNT,
    STRONG_HOUSE_THRESHOLD,
    VERY_STRONG_THRESHOLD,
    WEAK_HOUSE_THRESHOLD,
    AshtakavargaStrength,
    get_ashtakavarga_interpretation,
    get_bhinna_planet_interpretation,
    get_house_strength_classification,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_rasi_count():
    assert RASI_COUNT == 12


def test_houses_per_planet():
    assert HOUSES_PER_PLANET == 8


def test_max_avg_points():
    assert MAX_AVG_POINTS == 8


def test_strong_house_threshold():
    assert STRONG_HOUSE_THRESHOLD == 30


def test_weak_house_threshold():
    assert WEAK_HOUSE_THRESHOLD == 20


def test_very_strong_threshold():
    assert VERY_STRONG_THRESHOLD == 40


def test_benefic_planets_nonempty():
    assert len(BENEFIC_PLANETS) > 0


def test_malefic_planets_nonempty():
    assert len(MALEFIC_PLANETS) > 0


def test_planet_houses_has_standard_planets():
    for planet in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"):
        assert planet in PLANET_HOUSES


# ---------------------------------------------------------------------------
# AshtakavargaStrength enum
# ---------------------------------------------------------------------------


def test_strength_very_strong():
    assert AshtakavargaStrength.VERY_STRONG == "very_strong"


def test_strength_very_weak():
    assert AshtakavargaStrength.VERY_WEAK == "very_weak"


def test_strength_moderate():
    assert AshtakavargaStrength.MODERATE == "moderate"


def test_strength_has_5_members():
    assert len(list(AshtakavargaStrength)) == 5


# ---------------------------------------------------------------------------
# get_house_strength_classification()
# ---------------------------------------------------------------------------


def test_classify_very_strong():
    assert get_house_strength_classification(45) == AshtakavargaStrength.VERY_STRONG


def test_classify_strong():
    assert get_house_strength_classification(35) == AshtakavargaStrength.STRONG


def test_classify_moderate():
    assert get_house_strength_classification(25) == AshtakavargaStrength.MODERATE


def test_classify_weak():
    assert get_house_strength_classification(15) == AshtakavargaStrength.WEAK


def test_classify_very_weak():
    assert get_house_strength_classification(5) == AshtakavargaStrength.VERY_WEAK


def test_classify_boundary_very_strong():
    assert get_house_strength_classification(VERY_STRONG_THRESHOLD) == AshtakavargaStrength.VERY_STRONG


def test_classify_boundary_strong():
    assert get_house_strength_classification(STRONG_HOUSE_THRESHOLD) == AshtakavargaStrength.STRONG


def test_classify_boundary_weak():
    # 20 = WEAK boundary
    result = get_house_strength_classification(MODERATE_HOUSE_THRESHOLD)
    assert result in (AshtakavargaStrength.MODERATE, AshtakavargaStrength.WEAK)


# ---------------------------------------------------------------------------
# get_ashtakavarga_interpretation()
# ---------------------------------------------------------------------------


def test_get_ashtakavarga_interpretation_returns_str():
    result = get_ashtakavarga_interpretation(1, 35, AshtakavargaStrength.STRONG)
    assert isinstance(result, str) and len(result) > 0


def test_get_ashtakavarga_interpretation_very_weak():
    result = get_ashtakavarga_interpretation(8, 5, AshtakavargaStrength.VERY_WEAK)
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# get_bhinna_planet_interpretation()
# ---------------------------------------------------------------------------


def test_get_bhinna_planet_interpretation_returns_str():
    result = get_bhinna_planet_interpretation("jupiter", [4, 5, 3, 6, 4, 5, 3, 4, 5, 6, 4, 5])
    assert isinstance(result, str) and len(result) > 0
