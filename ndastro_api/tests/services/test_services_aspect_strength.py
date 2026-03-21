"""Unit tests for ndastro_api.services.aspect_strength."""

from ndastro_api.services.aspect_strength import (
    ASPECT_ORBS,
    MAX_ORB_STRENGTH,
    MIN_ORB_STRENGTH,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
    SPECIAL_ASPECT_STRENGTHS,
    AspectDetails,
    AspectQuality,
    AspectStrengthReport,
    AspectType,
    calculate_aspects_with_strength,
    get_applying_aspects,
    get_planet_aspects,
)

# ---------------------------------------------------------------------------
# AspectType enum
# ---------------------------------------------------------------------------


def test_aspect_type_conjunction():
    assert AspectType.CONJUNCTION == "conjunction"


def test_aspect_type_opposition():
    assert AspectType.OPPOSITION == "opposition"


def test_aspect_type_trine():
    assert AspectType.TRINE == "trine"


def test_aspect_type_square():
    assert AspectType.SQUARE == "square"


def test_aspect_type_has_members():
    assert len(list(AspectType)) > 0


# ---------------------------------------------------------------------------
# AspectQuality enum
# ---------------------------------------------------------------------------


def test_aspect_quality_benefic():
    assert AspectQuality.BENEFIC == "benefic"


def test_aspect_quality_malefic():
    assert AspectQuality.MALEFIC == "malefic"


def test_aspect_quality_neutral():
    assert AspectQuality.NEUTRAL == "neutral"


def test_aspect_quality_has_3_members():
    assert len(list(AspectQuality)) == 3


# ---------------------------------------------------------------------------
# ASPECT_ORBS
# ---------------------------------------------------------------------------


def test_aspect_orbs_has_conjunction():
    assert AspectType.CONJUNCTION in ASPECT_ORBS


def test_aspect_orbs_conjunction_value():
    assert ASPECT_ORBS[AspectType.CONJUNCTION] == 10.0


# ---------------------------------------------------------------------------
# SPECIAL_ASPECT_STRENGTHS
# ---------------------------------------------------------------------------


def test_special_aspects_has_mars():
    assert "Mars" in SPECIAL_ASPECT_STRENGTHS


def test_special_aspects_has_jupiter():
    assert "Jupiter" in SPECIAL_ASPECT_STRENGTHS


def test_special_aspects_has_saturn():
    assert "Saturn" in SPECIAL_ASPECT_STRENGTHS


# ---------------------------------------------------------------------------
# NATURAL_BENEFICS and NATURAL_MALEFICS
# ---------------------------------------------------------------------------


def test_natural_benefics_has_jupiter():
    assert "Jupiter" in NATURAL_BENEFICS


def test_natural_malefics_has_saturn():
    assert "Saturn" in NATURAL_MALEFICS


def test_min_max_orb_strength():
    assert MIN_ORB_STRENGTH < MAX_ORB_STRENGTH


# ---------------------------------------------------------------------------
# calculate_aspects_with_strength()
# ---------------------------------------------------------------------------

_SAMPLE_LONGITUDES = {
    "Sun": 0.0,
    "Moon": 120.0,
    "Mars": 90.0,
    "Mercury": 10.0,
    "Jupiter": 240.0,
    "Venus": 60.0,
    "Saturn": 180.0,
}


def test_calculate_aspects_returns_report():
    report = calculate_aspects_with_strength(_SAMPLE_LONGITUDES)
    assert isinstance(report, AspectStrengthReport)


def test_calculate_aspects_has_aspects_list():
    report = calculate_aspects_with_strength(_SAMPLE_LONGITUDES)
    assert isinstance(report.aspects, list)


def test_calculate_aspects_strongest_list():
    report = calculate_aspects_with_strength(_SAMPLE_LONGITUDES)
    assert isinstance(report.strongest_aspects, list)


def test_calculate_aspects_benefic_malefic_lists():
    report = calculate_aspects_with_strength(_SAMPLE_LONGITUDES)
    assert isinstance(report.benefic_aspects, list)
    assert isinstance(report.malefic_aspects, list)


def test_calculate_aspects_details_are_dataclass():
    report = calculate_aspects_with_strength(_SAMPLE_LONGITUDES)
    for asp in report.aspects:
        assert isinstance(asp, AspectDetails)


def test_calculate_aspects_orb_in_range():
    report = calculate_aspects_with_strength(_SAMPLE_LONGITUDES)
    for asp in report.aspects:
        assert asp.orb >= 0.0


def test_calculate_aspects_with_threshold():
    report = calculate_aspects_with_strength(_SAMPLE_LONGITUDES, min_strength_threshold=0.5)
    # All returned aspects should meet the threshold
    for asp in report.aspects:
        assert asp.orb_strength >= 0.5


# ---------------------------------------------------------------------------
# get_planet_aspects()
# ---------------------------------------------------------------------------


def test_get_planet_aspects_returns_sequence():
    report = calculate_aspects_with_strength(_SAMPLE_LONGITUDES)
    result = get_planet_aspects(report, "Sun")
    assert hasattr(result, "__iter__")


def test_get_planet_aspects_all_involve_planet():
    report = calculate_aspects_with_strength(_SAMPLE_LONGITUDES)
    result = list(get_planet_aspects(report, "Jupiter"))
    for asp in result:
        assert asp.aspecting_planet == "Jupiter" or asp.aspected_planet == "Jupiter"


# ---------------------------------------------------------------------------
# get_applying_aspects()
# ---------------------------------------------------------------------------


def test_get_applying_aspects_returns_sequence():
    report = calculate_aspects_with_strength(
        _SAMPLE_LONGITUDES,
        planet_speeds={"Sun": 1.0, "Moon": 13.0, "Mars": 0.5, "Mercury": 1.3, "Jupiter": 0.08, "Venus": 1.2, "Saturn": 0.03},
    )
    result = get_applying_aspects(report)
    assert hasattr(result, "__iter__")


def test_get_applying_aspects_all_are_applying():
    report = calculate_aspects_with_strength(
        _SAMPLE_LONGITUDES,
        planet_speeds={"Sun": 1.0, "Moon": 13.0, "Mars": 0.5, "Mercury": 1.3, "Jupiter": 0.08, "Venus": 1.2, "Saturn": 0.03},
    )
    for asp in get_applying_aspects(report):
        assert asp.is_applying is True
