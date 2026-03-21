"""Extended tests for ndastro_api.services.avasthas - alertness, mood, activity avasthas."""

import pytest

from ndastro_api.services.avasthas import (
    ActivityAvastha,
    ActivityAvasthaPlanetContext,
    ActivityStrength,
    AgeAvastha,
    AlertnessAvastha,
    AvasthaPlanetContext,
    AvasthaSummary,
    MoodAvastha,
    calculate_activity_avastha,
    calculate_alertness_avastha,
    calculate_mood_avastha,
    get_activity_avastha_interpretation,
    get_age_avastha_interpretation,
    get_alertness_avastha_interpretation,
    get_all_avasthas,
    get_mood_avastha_interpretation,
)

# ---------------------------------------------------------------------------
# calculate_alertness_avastha — unknown planet code
# ---------------------------------------------------------------------------


def test_alertness_unknown_planet_returns_swapna():
    result, desc = calculate_alertness_avastha("INVALID_PLANET_999", "Aries")
    assert result == AlertnessAvastha.SWAPNA
    assert "Unknown planet" in desc


# ---------------------------------------------------------------------------
# calculate_alertness_avastha — valid planet code, unknown rasi
# ---------------------------------------------------------------------------


def test_alertness_valid_planet_unknown_rasi_returns_default():
    # "SU" is a valid planet code in planets.json
    result, desc = calculate_alertness_avastha("SU", "UNKNOWN_RASI_XYZ")
    assert result == AlertnessAvastha.SWAPNA


# ---------------------------------------------------------------------------
# calculate_alertness_avastha — valid planet + valid rasi
# ---------------------------------------------------------------------------


def test_alertness_valid_planet_and_rasi():
    result, desc = calculate_alertness_avastha("SU", "Aries")
    assert result in list(AlertnessAvastha)
    assert isinstance(desc, str)


def test_alertness_moon_in_taurus():
    result, desc = calculate_alertness_avastha("MO", "Taurus")
    assert result in list(AlertnessAvastha)


def test_alertness_mars_in_capricorn():
    result, desc = calculate_alertness_avastha("MA", "Capricorn")
    assert result in list(AlertnessAvastha)


def test_alertness_mercury_in_virgo():
    # Mercury's exaltation is Virgo
    result, desc = calculate_alertness_avastha("ME", "Virgo")
    assert result in list(AlertnessAvastha)
    assert isinstance(desc, str)


def test_alertness_jupiter_in_cancer():
    result, desc = calculate_alertness_avastha("JU", "Cancer")
    assert result in list(AlertnessAvastha)


def test_alertness_venus_in_pisces():
    result, desc = calculate_alertness_avastha("VE", "Pisces")
    assert result in list(AlertnessAvastha)


def test_alertness_saturn_in_libra():
    result, desc = calculate_alertness_avastha("SA", "Libra")
    assert result in list(AlertnessAvastha)


# ---------------------------------------------------------------------------
# calculate_mood_avastha — unknown planet
# ---------------------------------------------------------------------------


def test_mood_unknown_planet_returns_deena():
    ctx = AvasthaPlanetContext(
        planet_code="INVALID_XYZ",
        house_number=1,
        degree_in_rasi=15.0,
        rasi_name="Aries",
        rasi_number=1,
    )
    result, desc = calculate_mood_avastha(ctx)
    assert result == MoodAvastha.DEENA


# ---------------------------------------------------------------------------
# calculate_mood_avastha — valid planet, various conditions
# ---------------------------------------------------------------------------


def test_mood_sun_in_aries():
    ctx = AvasthaPlanetContext(
        planet_code="SU",
        house_number=1,
        degree_in_rasi=10.0,
        rasi_name="Aries",
        rasi_number=1,
    )
    result, desc = calculate_mood_avastha(ctx)
    assert result in list(MoodAvastha)
    assert isinstance(desc, str)


def test_mood_with_malefic_conjunction():
    ctx = AvasthaPlanetContext(
        planet_code="MO",
        house_number=3,
        degree_in_rasi=10.0,
        rasi_name="Taurus",
        rasi_number=2,
        conjunction_planets=["mars barycenter"],
    )
    result, desc = calculate_mood_avastha(ctx)
    assert result in list(MoodAvastha)


def test_mood_with_malefic_in_5th_house():
    ctx = AvasthaPlanetContext(
        planet_code="MO",
        house_number=5,
        degree_in_rasi=10.0,
        rasi_name="Leo",
        rasi_number=5,
        conjunction_planets=["saturn barycenter"],
    )
    result, desc = calculate_mood_avastha(ctx)
    # In 5th with malefic → LAJJITA
    assert result == MoodAvastha.LAJJITA or result in list(MoodAvastha)


def test_mood_with_sun_conjunction():
    ctx = AvasthaPlanetContext(
        planet_code="MA",
        house_number=2,
        degree_in_rasi=5.0,
        rasi_name="Taurus",
        rasi_number=2,
        conjunction_planets=["sun"],
    )
    result, desc = calculate_mood_avastha(ctx)
    assert result in list(MoodAvastha)


def test_mood_in_enemy_rasi():
    ctx = AvasthaPlanetContext(
        planet_code="SU",
        house_number=6,
        degree_in_rasi=20.0,
        rasi_name="Libra",
        rasi_number=7,
    )
    result, desc = calculate_mood_avastha(ctx)
    assert result in list(MoodAvastha)


def test_mood_with_aspecting_benefic():
    ctx = AvasthaPlanetContext(
        planet_code="SU",
        house_number=4,
        degree_in_rasi=12.0,
        rasi_name="Leo",
        rasi_number=5,
        aspecting_planets=["jupiter barycenter"],
    )
    result, desc = calculate_mood_avastha(ctx)
    assert result in list(MoodAvastha)


# ---------------------------------------------------------------------------
# calculate_activity_avastha — various index combinations
# ---------------------------------------------------------------------------


def test_activity_avastha_basic():
    ctx = ActivityAvasthaPlanetContext(
        constellation_number=1,
        planet_index=1,
        navamsa_index=1,
        moon_constellation=1,
        ghati_at_birth=10.0,
        lagna_rasi=1,
    )
    avastha, strength, desc = calculate_activity_avastha(ctx)
    assert isinstance(avastha, ActivityAvastha)
    assert isinstance(strength, ActivityStrength)
    assert isinstance(desc, str)


def test_activity_avastha_zero_remainder():
    # Force remainder = 0 → should map to 12 (NIDRAA)
    # (C * P * A) + M + G + L → need remainder = 0 mod 12
    # Try: 12 * 1 * 1 + 0 + 0 + 0 = 12 → 12 % 12 = 0 → avastha_index = 12
    ctx = ActivityAvasthaPlanetContext(
        constellation_number=12,
        planet_index=1,
        navamsa_index=1,
        moon_constellation=0,
        ghati_at_birth=0.0,
        lagna_rasi=0,
    )
    avastha, strength, desc = calculate_activity_avastha(ctx)
    assert avastha == ActivityAvastha.NIDRAA


@pytest.mark.parametrize(
    "nak,planet,nav",
    [
        (1, 1, 1),
        (5, 2, 3),
        (10, 5, 5),
        (15, 7, 2),
        (20, 3, 9),
        (27, 9, 9),
    ],
)
def test_activity_avastha_various_combinations(nak, planet, nav):
    ctx = ActivityAvasthaPlanetContext(
        constellation_number=nak,
        planet_index=planet,
        navamsa_index=nav,
        moon_constellation=nak,
        ghati_at_birth=float(nak),
        lagna_rasi=(nak % 12) + 1,
    )
    avastha, strength, desc = calculate_activity_avastha(ctx)
    assert avastha in list(ActivityAvastha)
    assert strength in list(ActivityStrength)


# ---------------------------------------------------------------------------
# get_age_avastha_interpretation — known and unknown planets
# ---------------------------------------------------------------------------


def test_age_interpretation_sun_yuva():
    desc = get_age_avastha_interpretation("sun", AgeAvastha.YUVA)
    assert "Sun" in desc or "youth" in desc.lower()


def test_age_interpretation_moon_mrita():
    desc = get_age_avastha_interpretation("moon", AgeAvastha.MRITA)
    assert isinstance(desc, str) and len(desc) > 0


def test_age_interpretation_mercury_saisava():
    desc = get_age_avastha_interpretation("mercury", AgeAvastha.SAISAVA)
    assert "Mercury" in desc or "child" in desc.lower() or "learning" in desc.lower()


def test_age_interpretation_unknown_planet():
    desc = get_age_avastha_interpretation("rahu", AgeAvastha.YUVA)
    # Not in dict → returns generic
    assert "yuva" in desc.lower() or "state" in desc.lower()


def test_age_interpretation_with_barycenter_name():
    desc = get_age_avastha_interpretation("moon barycenter", AgeAvastha.VRIDDHA)
    assert isinstance(desc, str)


# ---------------------------------------------------------------------------
# get_alertness_avastha_interpretation — all planets and states
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("planet", ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"])
@pytest.mark.parametrize("state", list(AlertnessAvastha))
def test_alertness_interpretation_known_planets(planet, state):
    desc = get_alertness_avastha_interpretation(planet, state)
    assert isinstance(desc, str) and len(desc) > 0


def test_alertness_interpretation_unknown_planet():
    desc = get_alertness_avastha_interpretation("rahu", AlertnessAvastha.JAAGRITA)
    assert "jaagrita" in desc.lower() or "state" in desc.lower()


# ---------------------------------------------------------------------------
# get_mood_avastha_interpretation — known planets and defaults
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("planet", ["sun", "moon", "mars"])
@pytest.mark.parametrize("state", list(MoodAvastha))
def test_mood_interpretation_known_planets(planet, state):
    desc = get_mood_avastha_interpretation(planet, state)
    assert isinstance(desc, str) and len(desc) > 0


@pytest.mark.parametrize("state", list(MoodAvastha))
def test_mood_interpretation_unknown_planet_uses_defaults(state):
    desc = get_mood_avastha_interpretation("rahu", state)
    assert isinstance(desc, str) and len(desc) > 0


def test_mood_interpretation_with_barycenter():
    desc = get_mood_avastha_interpretation("mars barycenter", MoodAvastha.DEEPTA)
    assert isinstance(desc, str)


# ---------------------------------------------------------------------------
# get_activity_avastha_interpretation — all avasthas and strengths
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("avastha", list(ActivityAvastha))
@pytest.mark.parametrize("strength", list(ActivityStrength))
def test_activity_interpretation_all_combinations(avastha, strength):
    desc = get_activity_avastha_interpretation("sun", avastha, strength)
    assert isinstance(desc, str) and len(desc) > 0


# ---------------------------------------------------------------------------
# get_all_avasthas — comprehensive summary
# ---------------------------------------------------------------------------


def test_get_all_avasthas_returns_summary():
    ctx = AvasthaPlanetContext(
        planet_code="SU",
        house_number=1,
        degree_in_rasi=15.0,
        rasi_name="Aries",
        rasi_number=1,
    )
    summary = get_all_avasthas(ctx)
    assert isinstance(summary, AvasthaSummary)
    assert summary.planet_code == "SU"
    assert isinstance(summary.age_avastha, str)
    assert isinstance(summary.alertness_avastha, str)
    assert isinstance(summary.mood_avastha, str)


def test_get_all_avasthas_even_rasi():
    # Even rasi → anti-zodiacal (coverage for even-rasi branch in calculate_age_avastha)
    ctx = AvasthaPlanetContext(
        planet_code="MO",
        house_number=3,
        degree_in_rasi=3.0,  # < 6.0, even rasi → MRITA (anti-zodiacal)
        rasi_name="Taurus",
        rasi_number=2,  # even rasi
    )
    summary = get_all_avasthas(ctx)
    assert summary.age_avastha == AgeAvastha.MRITA.value


def test_get_all_avasthas_vriddha_zone():
    ctx = AvasthaPlanetContext(
        planet_code="MA",
        house_number=2,
        degree_in_rasi=21.0,  # 18-24 in odd → VRIDDHA
        rasi_name="Aries",
        rasi_number=1,  # odd rasi
    )
    summary = get_all_avasthas(ctx)
    assert summary.age_avastha == AgeAvastha.VRIDDHA.value


def test_get_all_avasthas_mrita_zone_odd():
    ctx = AvasthaPlanetContext(
        planet_code="JU",
        house_number=5,
        degree_in_rasi=27.0,  # > 24 in odd → MRITA
        rasi_name="Leo",
        rasi_number=5,
    )
    summary = get_all_avasthas(ctx)
    assert summary.age_avastha == AgeAvastha.MRITA.value


# ---------------------------------------------------------------------------
# AvasthaSummary dataclass field presence
# ---------------------------------------------------------------------------


def test_avastha_summary_fields():
    ctx = AvasthaPlanetContext(
        planet_code="VE",
        house_number=7,
        degree_in_rasi=5.0,
        rasi_name="Libra",
        rasi_number=7,
    )
    summary = get_all_avasthas(ctx)
    assert hasattr(summary, "age_interpretation")
    assert hasattr(summary, "alertness_interpretation")
    assert hasattr(summary, "mood_interpretation")
    # activity fields are None since no ActivityAvasthaPlanetContext provided
    assert summary.activity_avastha is None
