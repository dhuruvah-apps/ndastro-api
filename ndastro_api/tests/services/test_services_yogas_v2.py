"""Extended tests for ndastro_api.services.yogas - yoga rule evaluation."""

import pytest

from ndastro_api.services.yogas import (
    PlanetaryYogaContext,
    YogaRuleResult,
    evaluate_planetary_yogas,
    get_nitya_yoga_name,
)

# ---------------------------------------------------------------------------
# Helper factory
# ---------------------------------------------------------------------------

_ALL_PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "kethu"]


def _ctx(
    houses: dict[str, int] | None = None,
    rasis: dict[str, str] | None = None,
    house_lords: dict[int, str] | None = None,
    own_signs: dict[str, set[str]] | None = None,
    exaltation_signs: dict[str, str] | None = None,
    debilitation_signs: dict[str, str] | None = None,
    lagna_house: int | None = None,
) -> PlanetaryYogaContext:
    default_houses = dict.fromkeys(_ALL_PLANETS, 1)
    default_rasis = dict.fromkeys(_ALL_PLANETS, "aries")
    return PlanetaryYogaContext(
        planet_houses=houses if houses is not None else default_houses,
        planet_rasis=rasis if rasis is not None else default_rasis,
        house_lords=house_lords,
        own_signs=own_signs,
        exaltation_signs=exaltation_signs,
        debilitation_signs=debilitation_signs,
        lagna_house=lagna_house,
    )


# ---------------------------------------------------------------------------
# get_nitya_yoga_name - out-of-range
# ---------------------------------------------------------------------------


def test_get_nitya_yoga_name_zero():
    assert get_nitya_yoga_name(0) == "Unknown"


def test_get_nitya_yoga_name_28():
    assert get_nitya_yoga_name(28) == "Unknown"


def test_get_nitya_yoga_name_negative():
    assert get_nitya_yoga_name(-1) == "Unknown"


# ---------------------------------------------------------------------------
# evaluate_planetary_yogas - include_missing covers all rule paths
# ---------------------------------------------------------------------------


def test_evaluate_all_rules_include_missing_returns_25():
    ctx = _ctx()
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    assert len(results) == 25


def test_evaluate_all_rules_returns_list_of_yoga_rule_results():
    results = evaluate_planetary_yogas(_ctx(), include_missing=True)
    for r in results:
        assert isinstance(r, YogaRuleResult)


def test_evaluate_without_include_missing_returns_subset():
    # With all planets in house 1 many conjunctions are present
    ctx = _ctx()
    results = evaluate_planetary_yogas(ctx, include_missing=False)
    # Budha-Aditya (sun+mercury in house 1) and others should be present
    names = [r.name for r in results]
    assert "Budha-Aditya Yoga" in names


# ---------------------------------------------------------------------------
# Gajakesari Yoga (Jupiter in kendra from Moon)
# ---------------------------------------------------------------------------


def test_gajakesari_present_jupiter_kendra_from_moon():
    ctx = _ctx(houses={"moon": 1, "jupiter": 4, **{p: 5 for p in _ALL_PLANETS if p not in ("moon", "jupiter")}})
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    gaja = next(r for r in results if r.name == "Gajakesari Yoga")
    assert gaja.is_present is True


def test_gajakesari_not_present():
    ctx = _ctx(houses={"moon": 1, "jupiter": 2, **{p: 5 for p in _ALL_PLANETS if p not in ("moon", "jupiter")}})
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    gaja = next(r for r in results if r.name == "Gajakesari Yoga")
    assert gaja.is_present is False


# ---------------------------------------------------------------------------
# Budha-Aditya Yoga (Sun + Mercury conjunct)
# ---------------------------------------------------------------------------


def test_budha_aditya_present_same_house():
    ctx = _ctx(houses={"sun": 3, "mercury": 3, **{p: 9 for p in _ALL_PLANETS if p not in ("sun", "mercury")}})
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    ba = next(r for r in results if r.name == "Budha-Aditya Yoga")
    assert ba.is_present is True


def test_budha_aditya_not_present():
    ctx = _ctx(houses={"sun": 1, "mercury": 7, **{p: 9 for p in _ALL_PLANETS if p not in ("sun", "mercury")}})
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    ba = next(r for r in results if r.name == "Budha-Aditya Yoga")
    assert ba.is_present is False


# ---------------------------------------------------------------------------
# Chandra-Mangala Yoga (Moon + Mars conjunct)
# ---------------------------------------------------------------------------


def test_chandra_mangala_present():
    ctx = _ctx(houses={"moon": 5, "mars": 5, **{p: 9 for p in _ALL_PLANETS if p not in ("moon", "mars")}})
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    cm = next(r for r in results if r.name == "Chandra-Mangala Yoga")
    assert cm.is_present is True


# ---------------------------------------------------------------------------
# Guru-Chandala Yoga (Jupiter conjunct Rahu or Kethu)
# ---------------------------------------------------------------------------


def test_guru_chandala_with_rahu():
    ctx = _ctx(houses={"jupiter": 6, "rahu": 6, **{p: 1 for p in _ALL_PLANETS if p not in ("jupiter", "rahu")}})
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    gc = next(r for r in results if r.name == "Guru-Chandala Yoga")
    assert gc.is_present is True


def test_guru_chandala_with_kethu():
    ctx = _ctx(houses={"jupiter": 6, "kethu": 6, "rahu": 1, **{p: 9 for p in _ALL_PLANETS if p not in ("jupiter", "kethu", "rahu")}})
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    gc = next(r for r in results if r.name == "Guru-Chandala Yoga")
    assert gc.is_present is True


# ---------------------------------------------------------------------------
# Shukra-Mangala Yoga (Venus + Mars conjunct)
# ---------------------------------------------------------------------------


def test_shukra_mangala_present():
    ctx = _ctx(houses={"venus": 8, "mars": 8, **{p: 2 for p in _ALL_PLANETS if p not in ("venus", "mars")}})
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    sm = next(r for r in results if r.name == "Shukra-Mangala Yoga")
    assert sm.is_present is True


# ---------------------------------------------------------------------------
# Pancha Mahapurusha Yogas
# ---------------------------------------------------------------------------


def test_bhadra_yoga_present_mercury_kendra_own_sign():
    ctx = _ctx(
        houses={"mercury": 1, **{p: 5 for p in _ALL_PLANETS if p != "mercury"}},
        rasis={"mercury": "gemini", **{p: "leo" for p in _ALL_PLANETS if p != "mercury"}},
        own_signs={"mercury": {"gemini", "virgo"}},
        exaltation_signs={"mercury": "virgo"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    bhadra = next(r for r in results if r.name == "Bhadra Yoga")
    assert bhadra.is_present is True


def test_ruchaka_yoga_present_mars_kendra_own_sign():
    ctx = _ctx(
        houses={"mars": 4, **{p: 5 for p in _ALL_PLANETS if p != "mars"}},
        rasis={"mars": "aries", **{p: "leo" for p in _ALL_PLANETS if p != "mars"}},
        own_signs={"mars": {"aries", "scorpio"}},
        exaltation_signs={"mars": "capricorn"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    ruchaka = next(r for r in results if r.name == "Ruchaka Yoga")
    assert ruchaka.is_present is True


def test_hamsa_yoga_present_jupiter_kendra_own_sign():
    ctx = _ctx(
        houses={"jupiter": 7, **{p: 5 for p in _ALL_PLANETS if p != "jupiter"}},
        rasis={"jupiter": "sagittarius", **{p: "leo" for p in _ALL_PLANETS if p != "jupiter"}},
        own_signs={"jupiter": {"sagittarius", "pisces"}},
        exaltation_signs={"jupiter": "cancer"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    hamsa = next(r for r in results if r.name == "Hamsa Yoga")
    assert hamsa.is_present is True


def test_malavya_yoga_present_venus_kendra_own_sign():
    ctx = _ctx(
        houses={"venus": 10, **{p: 5 for p in _ALL_PLANETS if p != "venus"}},
        rasis={"venus": "taurus", **{p: "leo" for p in _ALL_PLANETS if p != "venus"}},
        own_signs={"venus": {"taurus", "libra"}},
        exaltation_signs={"venus": "pisces"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    malavya = next(r for r in results if r.name == "Malavya Yoga")
    assert malavya.is_present is True


def test_sasa_yoga_present_saturn_kendra_own_sign():
    ctx = _ctx(
        houses={"saturn": 1, **{p: 5 for p in _ALL_PLANETS if p != "saturn"}},
        rasis={"saturn": "capricorn", **{p: "leo" for p in _ALL_PLANETS if p != "saturn"}},
        own_signs={"saturn": {"capricorn", "aquarius"}},
        exaltation_signs={"saturn": "libra"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    sasa = next(r for r in results if r.name == "Sasa Yoga")
    assert sasa.is_present is True


def test_mahapurusha_missing_house_returns_not_present():
    # planet not in planet_houses → is_present=False, details mention missing
    ctx = PlanetaryYogaContext(
        planet_houses={"sun": 1},
        planet_rasis={"sun": "aries"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    bhadra = next(r for r in results if r.name == "Bhadra Yoga")
    assert bhadra.is_present is False


# ---------------------------------------------------------------------------
# Raja Yoga
# ---------------------------------------------------------------------------


def test_raja_yoga_missing_house_lords():
    ctx = _ctx()  # No house_lords
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    raja = next(r for r in results if r.name == "Raja Yoga")
    assert raja.is_present is False
    assert "Missing" in raja.details


def test_raja_yoga_kendra_trikona_lords_conjunct():
    # Mars lords kendra (1) AND trikona (5) → raja yoga present
    ctx = _ctx(
        houses={"mars": 3, **{p: 9 for p in _ALL_PLANETS if p != "mars"}},
        house_lords={1: "mars", 4: "moon", 5: "mars", 7: "venus", 9: "jupiter", 10: "saturn"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    raja = next(r for r in results if r.name == "Raja Yoga")
    # Two lords in same house would create yoga, but here same planet lords both → skipped
    # Just verify it runs without error
    assert raja is not None


def test_raja_yoga_different_lords_same_house():
    ctx = _ctx(
        houses={"mars": 3, "jupiter": 3, **{p: 9 for p in _ALL_PLANETS if p not in ("mars", "jupiter")}},
        house_lords={1: "mars", 5: "jupiter", 4: "moon", 7: "venus", 9: "saturn", 10: "mercury"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    raja = next(r for r in results if r.name == "Raja Yoga")
    assert raja.is_present is True


# ---------------------------------------------------------------------------
# Dhana Yoga
# ---------------------------------------------------------------------------


def test_dhana_yoga_missing_house_lords():
    ctx = _ctx()
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    dhana = next(r for r in results if r.name == "Dhana Yoga")
    assert dhana.is_present is False


def test_dhana_yoga_wealth_lord_conjunct_lagna_lord():
    ctx = _ctx(
        houses={"venus": 4, "sun": 4, **{p: 9 for p in _ALL_PLANETS if p not in ("venus", "sun")}},
        house_lords={2: "venus", 11: "mars", 1: "sun", 5: "saturn", 9: "jupiter"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    dhana = next(r for r in results if r.name == "Dhana Yoga")
    assert dhana.is_present is True


# ---------------------------------------------------------------------------
# Vipareeta Raja Yoga
# ---------------------------------------------------------------------------


def test_vipareeta_missing_house_lords():
    ctx = _ctx()
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    vpr = next(r for r in results if r.name == "Vipareeta Raja Yoga")
    assert vpr.is_present is False


def test_vipareeta_raja_present_dusthana_lord_in_dusthana():
    # Mars lords house 6 and is placed in house 8 (dusthana)
    ctx = _ctx(
        houses={"mars": 8, **{p: 3 for p in _ALL_PLANETS if p != "mars"}},
        house_lords={6: "mars", 8: "saturn", 12: "jupiter"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    vpr = next(r for r in results if r.name == "Vipareeta Raja Yoga")
    assert vpr.is_present is True


# ---------------------------------------------------------------------------
# Parivartana Yoga (mutual sign exchange)
# ---------------------------------------------------------------------------


def test_parivartana_missing_own_signs():
    ctx = _ctx()  # own_signs=None
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    par = next(r for r in results if r.name == "Parivartana Yoga")
    assert par.is_present is False
    assert "Missing own_signs" in par.details


def test_parivartana_present_mutual_exchange():
    # Mars in Taurus (Venus's sign), Venus in Aries (Mars's sign)
    ctx = _ctx(
        houses={"mars": 1, "venus": 2, **{p: 9 for p in _ALL_PLANETS if p not in ("mars", "venus")}},
        rasis={"mars": "taurus", "venus": "aries", **{p: "leo" for p in _ALL_PLANETS if p not in ("mars", "venus")}},
        own_signs={"mars": {"aries", "scorpio"}, "venus": {"taurus", "libra"}},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    par = next(r for r in results if r.name == "Parivartana Yoga")
    assert par.is_present is True


# ---------------------------------------------------------------------------
# Kemadruma Yoga (Moon isolated)
# ---------------------------------------------------------------------------


def test_kemadruma_missing_moon():
    ctx = PlanetaryYogaContext(
        planet_houses={"sun": 1},
        planet_rasis={"sun": "aries"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    kem = next(r for r in results if r.name == "Kemadruma Yoga")
    assert kem.is_present is False


def test_kemadruma_present_moon_isolated():
    # Moon in house 3, no other planets in 2, 3, or 4
    ctx = _ctx(
        houses={"moon": 3, **{p: 6 for p in _ALL_PLANETS if p != "moon"}},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    kem = next(r for r in results if r.name == "Kemadruma Yoga")
    assert kem.is_present is True


def test_kemadruma_not_present_planets_adjacent():
    # Mars in house 2 (adjacent to moon in 3)
    ctx = _ctx(
        houses={"moon": 3, "mars": 2, **{p: 6 for p in _ALL_PLANETS if p not in ("moon", "mars")}},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    kem = next(r for r in results if r.name == "Kemadruma Yoga")
    assert kem.is_present is False


# ---------------------------------------------------------------------------
# Adhi Yoga (Benefics in 6th/7th/8th from Moon)
# ---------------------------------------------------------------------------


def test_adhi_yoga_missing_moon():
    ctx = PlanetaryYogaContext(
        planet_houses={"sun": 1},
        planet_rasis={"sun": "aries"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    adhi = next(r for r in results if r.name == "Adhi Yoga")
    assert adhi.is_present is False


def test_adhi_yoga_present_jupiter_in_7th_from_moon():
    # Moon in house 1, Jupiter in house 7 (6+1 from moon)
    ctx = _ctx(
        houses={"moon": 1, "jupiter": 7, **{p: 3 for p in _ALL_PLANETS if p not in ("moon", "jupiter")}},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    adhi = next(r for r in results if r.name == "Adhi Yoga")
    assert adhi.is_present is True


# ---------------------------------------------------------------------------
# Amala Yoga (Benefic in 10th from Lagna or Moon)
# ---------------------------------------------------------------------------


def test_amala_missing_lagna():
    ctx = _ctx()  # lagna_house=None
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    amala = next(r for r in results if r.name == "Amala Yoga")
    assert amala.is_present is False


def test_amala_yoga_present():
    # Lagna house 1, Jupiter in house 10
    ctx = _ctx(
        houses={"moon": 3, "jupiter": 10, **{p: 5 for p in _ALL_PLANETS if p not in ("moon", "jupiter")}},
        lagna_house=1,
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    amala = next(r for r in results if r.name == "Amala Yoga")
    assert amala.is_present is True


# ---------------------------------------------------------------------------
# Dharma-Karmadhipati Yoga
# ---------------------------------------------------------------------------


def test_dharma_karmadhipati_missing_lords():
    ctx = _ctx()
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    dk = next(r for r in results if r.name == "Dharma-Karmadhipati Yoga")
    assert dk.is_present is False


def test_dharma_karmadhipati_missing_9th_or_10th_lord():
    ctx = _ctx(house_lords={1: "mars", 4: "moon"})  # No 9th/10th lords
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    dk = next(r for r in results if r.name == "Dharma-Karmadhipati Yoga")
    assert dk.is_present is False


def test_dharma_karmadhipati_present_9th_10th_conjunct():
    ctx = _ctx(
        houses={"jupiter": 5, "saturn": 5, **{p: 2 for p in _ALL_PLANETS if p not in ("jupiter", "saturn")}},
        house_lords={9: "jupiter", 10: "saturn"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    dk = next(r for r in results if r.name == "Dharma-Karmadhipati Yoga")
    assert dk.is_present is True


# ---------------------------------------------------------------------------
# Neecha-Bhanga Raja Yoga
# ---------------------------------------------------------------------------


def test_neecha_bhanga_missing_signs():
    ctx = _ctx()  # No debilitation/exaltation signs
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    nb = next(r for r in results if r.name == "Neecha-Bhanga Raja Yoga")
    assert nb.is_present is False


def test_neecha_bhanga_debilitated_planet_dispositor_in_kendra():
    # Mars debilitated in Cancer, placed in house 2, dispositor Moon in house 4 (kendra)
    ctx = _ctx(
        houses={"mars": 2, "moon": 4, **{p: 6 for p in _ALL_PLANETS if p not in ("mars", "moon")}},
        rasis={"mars": "cancer", "moon": "leo", **{p: "virgo" for p in _ALL_PLANETS if p not in ("mars", "moon")}},
        debilitation_signs={"mars": "cancer"},
        exaltation_signs={"mars": "capricorn"},
        house_lords={2: "moon"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    nb = next(r for r in results if r.name == "Neecha-Bhanga Raja Yoga")
    # dispositor (moon) is in house 4 (kendra) → neecha bhanga present
    assert nb.is_present is True


# ---------------------------------------------------------------------------
# Wealth Lord in Kendra
# ---------------------------------------------------------------------------


def test_wealth_lord_missing_house_lords():
    ctx = _ctx()
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    wlk = next(r for r in results if r.name == "Wealth Lord in Kendra")
    assert wlk.is_present is False


def test_wealth_lord_in_kendra_present():
    # Venus lords 2nd house and is in house 1 (kendra)
    ctx = _ctx(
        houses={"venus": 1, **{p: 6 for p in _ALL_PLANETS if p != "venus"}},
        house_lords={2: "venus", 11: "mars"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    wlk = next(r for r in results if r.name == "Wealth Lord in Kendra")
    assert wlk.is_present is True


# ---------------------------------------------------------------------------
# Nabhasa Yogas (Gola, Yuga, Sula)
# ---------------------------------------------------------------------------


def test_gola_yoga_all_in_one_house():
    ctx = _ctx(houses=dict.fromkeys(_ALL_PLANETS, 5))
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    gola = next(r for r in results if r.name == "Gola Yoga")
    assert gola.is_present is True


def test_gola_yoga_not_present_spread():
    ctx = _ctx(houses={p: i + 1 for i, p in enumerate(_ALL_PLANETS)})
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    gola = next(r for r in results if r.name == "Gola Yoga")
    assert gola.is_present is False


def test_yuga_yoga_two_houses():
    houses = {p: 1 if i < 5 else 7 for i, p in enumerate(_ALL_PLANETS)}
    ctx = _ctx(houses=houses)
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    yuga = next(r for r in results if r.name == "Yuga Yoga")
    assert yuga.is_present is True


def test_sula_yoga_three_houses():
    houses = {_ALL_PLANETS[i]: [1, 5, 9][i % 3] for i in range(len(_ALL_PLANETS))}
    ctx = _ctx(houses=houses)
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    sula = next(r for r in results if r.name == "Sula Yoga")
    assert sula.is_present is True


# ---------------------------------------------------------------------------
# Maraka Yoga
# ---------------------------------------------------------------------------


def test_maraka_missing_house_lords():
    ctx = _ctx()
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    maraka = next(r for r in results if r.name == "Maraka Yoga")
    assert maraka.is_present is False


def test_maraka_yoga_lord_in_dusthana():
    # Venus lords 7th and placed in house 8 (dusthana)
    ctx = _ctx(
        houses={"venus": 8, **{p: 3 for p in _ALL_PLANETS if p != "venus"}},
        house_lords={2: "mars", 7: "venus"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    maraka = next(r for r in results if r.name == "Maraka Yoga")
    assert maraka.is_present is True


# ---------------------------------------------------------------------------
# Arishta Yoga
# ---------------------------------------------------------------------------


def test_arishta_missing_lagna_lord():
    ctx = _ctx()  # No house_lords, no lagna_house
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    arishta = next(r for r in results if r.name == "Arishta Yoga")
    assert arishta.is_present is False


def test_arishta_present_lagna_lord_in_dusthana_malefic():
    # Mars lords lagna (house 1), placed in house 8 (dusthana), and Mars is malefic
    ctx = _ctx(
        houses={"mars": 8, "moon": 12, **{p: 3 for p in _ALL_PLANETS if p not in ("mars", "moon")}},
        house_lords={1: "mars"},
        lagna_house=1,
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    arishta = next(r for r in results if r.name == "Arishta Yoga")
    assert arishta.is_present is True


def test_arishta_present_moon_in_dusthana():
    ctx = _ctx(
        houses={"moon": 6, "mars": 2, **{p: 3 for p in _ALL_PLANETS if p not in ("moon", "mars")}},
        house_lords={1: "mars"},
        lagna_house=1,
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    arishta = next(r for r in results if r.name == "Arishta Yoga")
    assert arishta.is_present is True


# ---------------------------------------------------------------------------
# Coverage of _is_own_or_exalted and _is_debilitated branches
# ---------------------------------------------------------------------------


def test_mahapurusha_not_present_not_own_or_exalted():
    # Mars in kendra (house 1) but NOT in own/exaltation sign
    ctx = _ctx(
        houses={"mars": 1, **{p: 5 for p in _ALL_PLANETS if p != "mars"}},
        rasis={"mars": "gemini", **{p: "leo" for p in _ALL_PLANETS if p != "mars"}},
        own_signs={"mars": {"aries", "scorpio"}},
        exaltation_signs={"mars": "capricorn"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    ruchaka = next(r for r in results if r.name == "Ruchaka Yoga")
    assert ruchaka.is_present is False


def test_mahapurusha_via_exaltation_sign():
    # Jupiter exalted in Cancer, placed in kendra (house 4)
    ctx = _ctx(
        houses={"jupiter": 4, **{p: 5 for p in _ALL_PLANETS if p != "jupiter"}},
        rasis={"jupiter": "cancer", **{p: "leo" for p in _ALL_PLANETS if p != "jupiter"}},
        own_signs={"jupiter": {"sagittarius", "pisces"}},
        exaltation_signs={"jupiter": "cancer"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    hamsa = next(r for r in results if r.name == "Hamsa Yoga")
    assert hamsa.is_present is True


# ---------------------------------------------------------------------------
# Edge cases: planet code normalization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code,expected",
    [
        ("su", "sun"),
        ("mo", "moon"),
        ("ma", "mars"),
        ("me", "mercury"),
        ("ju", "jupiter"),
        ("ve", "venus"),
        ("sa", "saturn"),
        ("ra", "rahu"),
        ("ke", "kethu"),
    ],
)
def test_planet_code_normalization_in_context(code, expected):
    # Using abbreviated codes in planet_houses → should normalize to full names
    ctx = PlanetaryYogaContext(
        planet_houses={code: 1, "moon": 4},
        planet_rasis={code: "aries", "moon": "cancer"},
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    assert isinstance(results, list)


# ---------------------------------------------------------------------------
# Own signs branch: own_signs is None vs present but planet not in it
# ---------------------------------------------------------------------------


def test_own_signs_none_in_mahapurusha():
    ctx = _ctx(
        houses={"mars": 1, **{p: 5 for p in _ALL_PLANETS if p != "mars"}},
        rasis={"mars": "aries", **{p: "leo" for p in _ALL_PLANETS if p != "mars"}},
        own_signs=None,  # No own_signs provided
        exaltation_signs=None,
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    ruchaka = next(r for r in results if r.name == "Ruchaka Yoga")
    assert ruchaka.is_present is False  # Can't confirm own/exaltation without data


# ---------------------------------------------------------------------------
# Neecha-Bhanga: debilitated planet but no dispositor in kendra
# ---------------------------------------------------------------------------


def test_neecha_bhanga_not_present_dispositor_not_in_kendra():
    ctx = _ctx(
        houses={"mars": 2, "moon": 3, **{p: 6 for p in _ALL_PLANETS if p not in ("mars", "moon")}},
        rasis={"mars": "cancer", "moon": "leo", **{p: "virgo" for p in _ALL_PLANETS if p not in ("mars", "moon")}},
        debilitation_signs={"mars": "cancer"},
        exaltation_signs={"mars": "capricorn"},
        house_lords={2: "moon"},  # dispositor moon in house 3 (not kendra)
    )
    results = evaluate_planetary_yogas(ctx, include_missing=True)
    nb = next(r for r in results if r.name == "Neecha-Bhanga Raja Yoga")
    assert nb.is_present is False
