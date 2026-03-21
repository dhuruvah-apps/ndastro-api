"""Unit tests for ndastro_api.services.vimshopaka_bala."""

from ndastro_api.services.vimshopaka_bala import (
    DASAVARGA_WEIGHTS,
    DEBILITATION_SIGNS,
    DIGNITY_SCORES,
    EXALTATION_SIGNS,
    OWN_SIGNS,
    SAPTAVARGA_WEIGHTS,
    SHADVARGA_WEIGHTS,
    SHODASAVARGA_WEIGHTS,
    VimshopakaBalaReport,
    VimshopakaDignity,
    compute_vimshopaka_bala,
    get_dignity,
    get_strength_label,
)

# ---------------------------------------------------------------------------
# VimshopakaDignity enum
# ---------------------------------------------------------------------------


def test_dignity_exaltation():
    assert VimshopakaDignity.EXALTATION == "exaltation"


def test_dignity_debilitation():
    assert VimshopakaDignity.DEBILITATION == "debilitation"


def test_dignity_own_sign():
    assert VimshopakaDignity.OWN_SIGN == "own_sign"


def test_dignity_neutral():
    assert VimshopakaDignity.NEUTRAL == "neutral"


def test_dignity_has_9_members():
    assert len(list(VimshopakaDignity)) == 9


# ---------------------------------------------------------------------------
# Sign tables
# ---------------------------------------------------------------------------


def test_exaltation_signs_has_standard_planets():
    for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        assert planet in EXALTATION_SIGNS


def test_debilitation_signs_has_standard_planets():
    for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        assert planet in DEBILITATION_SIGNS


def test_exaltation_debilitation_differ():
    # Exaltation and debilitation are never the same sign
    for planet in ("Sun", "Moon", "Mars"):
        assert EXALTATION_SIGNS[planet] != DEBILITATION_SIGNS[planet]


def test_own_signs_has_standard_planets():
    for planet in ("Sun", "Moon", "Mars", "Jupiter", "Venus", "Saturn"):
        assert planet in OWN_SIGNS


# ---------------------------------------------------------------------------
# DIGNITY_SCORES
# ---------------------------------------------------------------------------


def test_dignity_scores_has_entries_for_all_dignities():
    for dignity in VimshopakaDignity:
        assert dignity in DIGNITY_SCORES


def test_dignity_scores_exaltation_highest():
    assert DIGNITY_SCORES[VimshopakaDignity.EXALTATION] >= DIGNITY_SCORES[VimshopakaDignity.OWN_SIGN]


def test_dignity_scores_debilitation_lowest():
    assert DIGNITY_SCORES[VimshopakaDignity.DEBILITATION] <= DIGNITY_SCORES[VimshopakaDignity.ENEMY]


# ---------------------------------------------------------------------------
# Scheme weight dicts
# ---------------------------------------------------------------------------


def test_shadvarga_has_6_entries():
    assert len(SHADVARGA_WEIGHTS) == 6


def test_saptavarga_has_7_entries():
    assert len(SAPTAVARGA_WEIGHTS) == 7


def test_dasavarga_has_10_entries():
    assert len(DASAVARGA_WEIGHTS) == 10


def test_shodasavarga_has_16_entries():
    assert len(SHODASAVARGA_WEIGHTS) == 16


# ---------------------------------------------------------------------------
# get_dignity()
# ---------------------------------------------------------------------------


def test_get_dignity_sun_in_aries():
    # Sun is exalted in Aries (rasi 1); keys are Title-cased
    dignity = get_dignity("Sun", EXALTATION_SIGNS["Sun"])
    assert dignity == VimshopakaDignity.EXALTATION


def test_get_dignity_sun_debilitated():
    dignity = get_dignity("Sun", DEBILITATION_SIGNS["Sun"])
    assert dignity == VimshopakaDignity.DEBILITATION


def test_get_dignity_in_own_sign():
    # Sun's own sign is Leo (rasi 5); keys are Title-cased
    own_sign_rasi = list(OWN_SIGNS.get("Sun", []))[0] if OWN_SIGNS.get("Sun") else None
    if own_sign_rasi is not None:
        dignity = get_dignity("Sun", own_sign_rasi)
        assert dignity in (VimshopakaDignity.OWN_SIGN, VimshopakaDignity.MOOLATRIKONA)


def test_get_dignity_returns_enum():
    result = get_dignity("Jupiter", 1)
    assert isinstance(result, VimshopakaDignity)


# ---------------------------------------------------------------------------
# compute_vimshopaka_bala()
# ---------------------------------------------------------------------------

_SAMPLE_LONGITUDES = {
    "sun": 0.0,  # Aries (exaltation)
    "moon": 30.0,  # Taurus
    "mars": 60.0,  # Gemini
    "mercury": 90.0,  # Cancer
    "jupiter": 120.0,  # Leo
    "venus": 150.0,  # Virgo
    "saturn": 180.0,  # Libra (exaltation)
    "rahu": 210.0,
    "kethu": 30.0,
}


def test_compute_vimshopaka_bala_returns_report():
    result = compute_vimshopaka_bala(_SAMPLE_LONGITUDES)
    assert isinstance(result, VimshopakaBalaReport)


def test_compute_vimshopaka_bala_default_scheme():
    result = compute_vimshopaka_bala(_SAMPLE_LONGITUDES)
    assert result.scheme == "shodasavarga"


def test_compute_vimshopaka_bala_scores_nonempty():
    result = compute_vimshopaka_bala(_SAMPLE_LONGITUDES)
    assert len(result.scores) > 0


def test_compute_vimshopaka_bala_shadvarga():
    result = compute_vimshopaka_bala(_SAMPLE_LONGITUDES, scheme="shadvarga")
    assert result.scheme == "shadvarga"


# ---------------------------------------------------------------------------
# get_strength_label()
# ---------------------------------------------------------------------------


def test_get_strength_label_returns_str():
    result = compute_vimshopaka_bala(_SAMPLE_LONGITUDES)
    if result.scores:
        first_score = next(iter(result.scores.values()))
        label = get_strength_label(first_score)
        assert isinstance(label, str) and len(label) > 0
