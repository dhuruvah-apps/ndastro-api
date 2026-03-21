"""Unit tests for ndastro_api.services.avasthas."""

from ndastro_api.services.avasthas import (
    ACTIVITY_CYCLE,
    AGE_DEGREE_BOUNDARY_1,
    AGE_DEGREE_BOUNDARY_2,
    AGE_DEGREE_BOUNDARY_3,
    AGE_DEGREE_BOUNDARY_4,
    ActivityAvastha,
    AgeAvastha,
    AlertnessAvastha,
    AvasthaPlanetContext,
    MoodAvastha,
    calculate_age_avastha,
    get_age_avastha_interpretation,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_age_boundary_1():
    assert AGE_DEGREE_BOUNDARY_1 == 6.0


def test_age_boundary_2():
    assert AGE_DEGREE_BOUNDARY_2 == 12.0


def test_age_boundary_3():
    assert AGE_DEGREE_BOUNDARY_3 == 18.0


def test_age_boundary_4():
    assert AGE_DEGREE_BOUNDARY_4 == 24.0


def test_activity_cycle():
    assert ACTIVITY_CYCLE == 12


# ---------------------------------------------------------------------------
# AgeAvastha enum
# ---------------------------------------------------------------------------


def test_age_avastha_saisava():
    assert AgeAvastha.SAISAVA == "saisava"


def test_age_avastha_mrita():
    assert AgeAvastha.MRITA == "mrita"


def test_age_avastha_yuva():
    assert AgeAvastha.YUVA == "yuva"


def test_age_avastha_has_5_members():
    assert len(list(AgeAvastha)) == 5


# ---------------------------------------------------------------------------
# AlertnessAvastha enum
# ---------------------------------------------------------------------------


def test_alertness_jaagrita():
    assert AlertnessAvastha.JAAGRITA == "jaagrita"


def test_alertness_sushupta():
    assert AlertnessAvastha.SUSHUPTA == "sushupta"


# ---------------------------------------------------------------------------
# MoodAvastha enum
# ---------------------------------------------------------------------------


def test_mood_deepta():
    assert MoodAvastha.DEEPTA == "deepta"


def test_mood_has_14_members():
    assert len(list(MoodAvastha)) == 14


# ---------------------------------------------------------------------------
# ActivityAvastha enum
# ---------------------------------------------------------------------------


def test_activity_sayana():
    assert ActivityAvastha.SAYANA == "sayana"


def test_activity_has_12_members():
    assert len(list(ActivityAvastha)) == 12


# ---------------------------------------------------------------------------
# calculate_age_avastha() — odd rasi (1): zodiacal order
# ---------------------------------------------------------------------------


def test_age_avastha_saisava_odd_rasi():
    avastha, strength = calculate_age_avastha(3.0, 1)
    assert avastha == AgeAvastha.SAISAVA
    assert strength == 0.25


def test_age_avastha_kumaara_odd_rasi():
    avastha, strength = calculate_age_avastha(8.0, 1)
    assert avastha == AgeAvastha.KUMAARA
    assert strength == 0.50


def test_age_avastha_yuva_odd_rasi():
    avastha, strength = calculate_age_avastha(15.0, 1)
    assert avastha == AgeAvastha.YUVA
    assert strength == 1.0


def test_age_avastha_vriddha_odd_rasi():
    avastha, strength = calculate_age_avastha(21.0, 1)
    assert avastha == AgeAvastha.VRIDDHA
    assert strength == 0.5


def test_age_avastha_mrita_odd_rasi():
    avastha, strength = calculate_age_avastha(27.0, 1)
    assert avastha == AgeAvastha.MRITA
    assert strength == 0.0


# ---------------------------------------------------------------------------
# calculate_age_avastha() — even rasi (2): anti-zodiacal order
# ---------------------------------------------------------------------------


def test_age_avastha_mrita_even_rasi():
    # In even rasi, first 6° → MRITA
    avastha, _ = calculate_age_avastha(3.0, 2)
    assert avastha == AgeAvastha.MRITA


def test_age_avastha_yuva_even_rasi():
    # In even rasi, 12-18° → YUVA
    avastha, strength = calculate_age_avastha(15.0, 2)
    assert avastha == AgeAvastha.YUVA
    assert strength == 1.0


# ---------------------------------------------------------------------------
# get_age_avastha_interpretation()
# ---------------------------------------------------------------------------


def test_get_age_avastha_interpretation_returns_str():
    result = get_age_avastha_interpretation("sun", AgeAvastha.YUVA)
    assert isinstance(result, str) and len(result) > 0


def test_get_age_avastha_interpretation_mrita():
    result = get_age_avastha_interpretation("moon", AgeAvastha.MRITA)
    assert isinstance(result, str) and len(result) > 0
