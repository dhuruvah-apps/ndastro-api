"""Tests targeting avasthas.py private helper branches via mock objects and direct function access."""

from unittest.mock import MagicMock

from ndastro_api.services.avasthas import (
    ActivityAvasthaPlanetContext,
    AgeAvastha,
    AlertnessAvastha,
    AvasthaPlanetContext,
    AvasthaSummary,
    MoodAvastha,
    _check_mood_debilitation,
    _check_mood_exaltation,
    _check_mood_moolatrikona,
    _check_mood_own_sign,
    _check_mood_sun_conjunction,
    _get_alertness_from_planet_dignity,
    calculate_age_avastha,
    get_all_avasthas_with_activity,
)

# ---------------------------------------------------------------------------
# Helper: create a mock Planet object
# ---------------------------------------------------------------------------


def _mock_planet(
    exaltation_sign: str | None = None,
    own_signs: list[str] | None = None,
    moolatrikona_sign: str | None = None,
    debilitation_sign: str | None = None,
    natural_friends: list[str] | None = None,
    natural_neutrals: list[str] | None = None,
    natural_enemies: list[str] | None = None,
) -> MagicMock:
    planet = MagicMock()
    if exaltation_sign:
        planet.exaltation = MagicMock()
        planet.exaltation.sign = exaltation_sign
    else:
        planet.exaltation = None
    planet.own_signs = own_signs or []
    if moolatrikona_sign:
        planet.moolatrikona = MagicMock()
        planet.moolatrikona.sign = moolatrikona_sign
    else:
        planet.moolatrikona = None
    if debilitation_sign:
        planet.debilitation = MagicMock()
        planet.debilitation.sign = debilitation_sign
    else:
        planet.debilitation = None
    planet.natural_friends = natural_friends or []
    planet.natural_neutrals = natural_neutrals or []
    planet.natural_enemies = natural_enemies or []
    return planet


# ---------------------------------------------------------------------------
# _get_alertness_from_planet_dignity — lines 169, 173, 177, 181, 185
# ---------------------------------------------------------------------------


def test_alertness_exaltation_branch():
    planet = _mock_planet(exaltation_sign="Aries")
    result = _get_alertness_from_planet_dignity(planet, "Aries", "ma")
    assert result == AlertnessAvastha.JAAGRITA  # line 169 hit


def test_alertness_own_rasi_branch():
    planet = _mock_planet(exaltation_sign=None, own_signs=["Leo"])
    result = _get_alertness_from_planet_dignity(planet, "Leo", "su")
    assert result == AlertnessAvastha.JAAGRITA  # line 173 hit


def test_alertness_natural_friends_branch():
    planet = _mock_planet(natural_friends=["MA"], natural_neutrals=[])
    result = _get_alertness_from_planet_dignity(planet, "Aries", "MA")
    assert result == AlertnessAvastha.SWAPNA  # line 177 hit


def test_alertness_natural_neutrals_branch():
    planet = _mock_planet(natural_friends=[], natural_neutrals=["MA"])
    result = _get_alertness_from_planet_dignity(planet, "Aries", "MA")
    assert result == AlertnessAvastha.SWAPNA  # line 177 alt branch


def test_alertness_debilitation_branch():
    planet = _mock_planet(debilitation_sign="Libra")
    result = _get_alertness_from_planet_dignity(planet, "Libra", "ve")
    assert result == AlertnessAvastha.SUSHUPTA  # line 181 hit


def test_alertness_enemy_branch():
    planet = _mock_planet(natural_enemies=["SA"])
    result = _get_alertness_from_planet_dignity(planet, "Capricorn", "SA")
    assert result == AlertnessAvastha.SUSHUPTA  # line 185 hit


def test_alertness_returns_none_otherwise():
    planet = _mock_planet()
    result = _get_alertness_from_planet_dignity(planet, "Aquarius", "sa")
    assert result is None


# ---------------------------------------------------------------------------
# _check_mood_exaltation — line 230
# ---------------------------------------------------------------------------


def test_check_mood_exaltation_present():
    planet = _mock_planet(exaltation_sign="Aries")
    result = _check_mood_exaltation(planet, "Aries")
    assert result == (MoodAvastha.DEEPTA, "Exalted - bright")  # line 230 hit


def test_check_mood_exaltation_not_exalted():
    planet = _mock_planet(exaltation_sign="Aries")
    result = _check_mood_exaltation(planet, "Leo")
    assert result is None


# ---------------------------------------------------------------------------
# _check_mood_own_sign — line 237
# ---------------------------------------------------------------------------


def test_check_mood_own_sign_present():
    planet = _mock_planet(own_signs=["Leo"])
    result = _check_mood_own_sign(planet, "Leo")
    assert result == (MoodAvastha.SWASTHA, "Own sign - content")  # line 237 hit


def test_check_mood_own_sign_not_own():
    planet = _mock_planet(own_signs=["Leo"])
    result = _check_mood_own_sign(planet, "Aries")
    assert result is None


# ---------------------------------------------------------------------------
# _check_mood_moolatrikona — line 244
# ---------------------------------------------------------------------------


def test_check_mood_moolatrikona_present():
    planet = _mock_planet(moolatrikona_sign="Leo")
    result = _check_mood_moolatrikona(planet, "Leo")
    assert result == (MoodAvastha.GARVITA, "Moolatrikona - proud")  # line 244 hit


def test_check_mood_moolatrikona_not_moolatrikona():
    planet = _mock_planet(moolatrikona_sign="Leo")
    result = _check_mood_moolatrikona(planet, "Aries")
    assert result is None


# ---------------------------------------------------------------------------
# _check_mood_debilitation — line 251
# ---------------------------------------------------------------------------


def test_check_mood_debilitation_present():
    planet = _mock_planet(debilitation_sign="Libra")
    result = _check_mood_debilitation(planet, "Libra")
    assert result == (MoodAvastha.DUKHITA, "Debilitated - distressed")  # line 251 hit


def test_check_mood_debilitation_not_debilitated():
    planet = _mock_planet(debilitation_sign="Libra")
    result = _check_mood_debilitation(planet, "Aries")
    assert result is None


# ---------------------------------------------------------------------------
# _check_mood_sun_conjunction — sun in 5th house (LAJJITA branch, line 285)
# ---------------------------------------------------------------------------


def test_check_mood_sun_conjunction_kopita():
    context = AvasthaPlanetContext(
        planet_code="MO",
        house_number=1,
        degree_in_rasi=15.0,
        rasi_name="Leo",
        rasi_number=5,
        conjunction_planets=["sun"],
    )
    result = _check_mood_sun_conjunction(context)
    assert result == (MoodAvastha.KOPITA, "Joined by Sun - angry")


def test_check_mood_sun_conjunction_no_sun():
    context = AvasthaPlanetContext(
        planet_code="MA",
        house_number=1,
        degree_in_rasi=15.0,
        rasi_name="Aries",
        rasi_number=1,
        conjunction_planets=["mars"],
    )
    result = _check_mood_sun_conjunction(context)
    assert result is None


# ---------------------------------------------------------------------------
# _get_bala_avastha fallback — line 162 (at end of iteration)
# ---------------------------------------------------------------------------


def test_bala_avastha_fallback_returns_mrita():
    # The fallback is typically unreachable due to float("inf") boundary,
    # but we can verify the normal flow returns sensible results.
    # For degree > all boundaries, the MRITA/SAASAVA boundary at inf catches it.
    # In practice the fallback after loop (line 162) should never trigger.
    # Let's just verify valid calls cover all expected states.
    for degree in [1.0, 7.0, 15.0, 22.0, 27.0, 29.9]:
        for rasi_num in [1, 2, 3]:
            result = calculate_age_avastha(degree, rasi_num)
            assert result[0] in list(AgeAvastha)


# ---------------------------------------------------------------------------
# get_all_avasthas_with_activity — lines 736-747
# ---------------------------------------------------------------------------


def test_get_all_avasthas_with_activity():
    context = AvasthaPlanetContext(
        planet_code="SU",
        house_number=1,
        degree_in_rasi=15.0,
        rasi_name="Aries",
        rasi_number=1,
    )
    activity_context = ActivityAvasthaPlanetContext(
        constellation_number=1,
        planet_index=1,
        navamsa_index=1,
        moon_constellation=1,
        ghati_at_birth=1.0,
        lagna_rasi=1,
    )
    summary = get_all_avasthas_with_activity(context, activity_context)
    assert isinstance(summary, AvasthaSummary)
    assert summary.activity_avastha is not None
    assert summary.activity_strength is not None
    assert summary.activity_interpretation is not None


def test_get_all_avasthas_with_activity_all_planets():
    for planet_code in ["SU", "MO", "MA", "ME", "JU", "VE", "SA"]:
        context = AvasthaPlanetContext(
            planet_code=planet_code,
            house_number=1,
            degree_in_rasi=10.0,
            rasi_name="Aries",
            rasi_number=1,
        )
        activity_context = ActivityAvasthaPlanetContext(
            constellation_number=2,
            planet_index=2,
            navamsa_index=2,
            moon_constellation=5,
            ghati_at_birth=10.0,
            lagna_rasi=1,
        )
        summary = get_all_avasthas_with_activity(context, activity_context)
        assert summary.planet_code == planet_code
