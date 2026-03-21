"""Extended yoga_extended tests — covering is_present=True branches."""

from ndastro_api.services.yoga_extended import (
    _budha_aditya_strong_yoga,
    _chamara_yoga,
    _kahala_yoga,
    _parvata_yoga,
    _sankha_yoga,
    evaluate_extended_yogas,
)
from ndastro_api.services.yogas import PlanetaryYogaContext


def _ctx(
    planet_houses: dict | None = None,
    planet_rasis: dict | None = None,
    house_lords: dict | None = None,
    exaltation_signs: dict | None = None,
) -> PlanetaryYogaContext:
    return PlanetaryYogaContext(
        planet_houses=planet_houses or {},
        planet_rasis=planet_rasis or {},
        house_lords=house_lords or {},
        exaltation_signs=exaltation_signs or {},
    )


# ---------------------------------------------------------------------------
# _budha_aditya_strong_yoga — lines 114-115 (is_present=True branch)
# ---------------------------------------------------------------------------


def test_budha_aditya_strong_present():
    context = _ctx(planet_houses={"sun": 1, "mercury": 1})
    result = _budha_aditya_strong_yoga(context)
    assert result.is_present is True
    assert "house 1" in result.details


def test_budha_aditya_strong_house_5():
    context = _ctx(planet_houses={"sun": 5, "mercury": 5})
    result = _budha_aditya_strong_yoga(context)
    assert result.is_present is True


def test_budha_aditya_strong_absent_different_houses():
    context = _ctx(planet_houses={"sun": 1, "mercury": 2})
    result = _budha_aditya_strong_yoga(context)
    assert result.is_present is False


def test_budha_aditya_strong_absent_non_benefic_house():
    # house 3 is not in {1,2,5,9,10,11}
    context = _ctx(planet_houses={"sun": 3, "mercury": 3})
    result = _budha_aditya_strong_yoga(context)
    assert result.is_present is False


# ---------------------------------------------------------------------------
# _kahala_yoga — lines 156-164 (mutual kendra present branch)
# ---------------------------------------------------------------------------


def test_kahala_yoga_present():
    # 4th=sun in house 1, 9th=moon in house 4 → |1-4|=3, in {0,3,6,9}
    context = _ctx(
        planet_houses={"sun": 1, "moon": 4},
        house_lords={4: "sun", 9: "moon"},
    )
    result = _kahala_yoga(context)
    assert result.is_present is True
    assert "kendras" in result.details


def test_kahala_yoga_absent_not_mutual_kendra():
    # |1-2|=1, not in {0,3,6,9}
    context = _ctx(
        planet_houses={"sun": 1, "moon": 2},
        house_lords={4: "sun", 9: "moon"},
    )
    result = _kahala_yoga(context)
    assert result.is_present is False


def test_kahala_yoga_present_house_diff_9():
    # 4th=sun in house 1, 9th=moon in house 10 → |1-10|=9 in {0,3,6,9}
    context = _ctx(
        planet_houses={"sun": 1, "moon": 10},
        house_lords={4: "sun", 9: "moon"},
    )
    result = _kahala_yoga(context)
    assert result.is_present is True


# ---------------------------------------------------------------------------
# _chamara_yoga — lines 189-190 (exalted lagna lord in kendra)
# ---------------------------------------------------------------------------


def test_chamara_yoga_present():
    # Lagna lord = sun, sun rasi = Aries, exaltation_signs has sun=Aries, sun in house 1 (kendra)
    context = _ctx(
        planet_houses={"sun": 1, "jupiter": 5},
        planet_rasis={"sun": "Aries"},
        house_lords={1: "sun"},
        exaltation_signs={"sun": "Aries"},
    )
    result = _chamara_yoga(context)
    assert result.is_present is True


def test_chamara_yoga_absent_not_exalted():
    context = _ctx(
        planet_houses={"sun": 1},
        planet_rasis={"sun": "Leo"},
        house_lords={1: "sun"},
        exaltation_signs={"sun": "Aries"},
    )
    result = _chamara_yoga(context)
    assert result.is_present is False


# ---------------------------------------------------------------------------
# _sankha_yoga — lines 210-218 (mutual kendra present branch)
# ---------------------------------------------------------------------------


def test_sankha_yoga_present():
    # 5th=sun in house 1, 6th=moon in house 1 → |1-1|=0 in {0,3,6,9}
    context = _ctx(
        planet_houses={"sun": 1, "moon": 1},
        house_lords={5: "sun", 6: "moon"},
    )
    result = _sankha_yoga(context)
    assert result.is_present is True


def test_sankha_yoga_present_diff_6():
    # 5th=sun in house 1, 6th=moon in house 7 → |1-7|=6 in {0,3,6,9}
    context = _ctx(
        planet_houses={"sun": 1, "moon": 7},
        house_lords={5: "sun", 6: "moon"},
    )
    result = _sankha_yoga(context)
    assert result.is_present is True


def test_sankha_yoga_absent():
    # |1-2|=1, not in {0,3,6,9}
    context = _ctx(
        planet_houses={"sun": 1, "moon": 2},
        house_lords={5: "sun", 6: "moon"},
    )
    result = _sankha_yoga(context)
    assert result.is_present is False


# ---------------------------------------------------------------------------
# _parvata_yoga — no malefics in kendra
# ---------------------------------------------------------------------------


def test_parvata_yoga_benefics_only_in_kendra():
    # Only jupiter (benefic) in kendra (house 1)
    context = _ctx(planet_houses={"jupiter": 1, "venus": 1})
    result = _parvata_yoga(context)
    # No malefics → yoga may be present
    assert result.name == "Parvata Yoga"


def test_parvata_yoga_malefic_in_kendra():
    # mars (malefic) in kendra → yoga absent
    context = _ctx(planet_houses={"mars": 1, "jupiter": 1})
    result = _parvata_yoga(context)
    assert result.is_present is False


# ---------------------------------------------------------------------------
# evaluate_extended_yogas — comprehensive check with Budha-Aditya present
# ---------------------------------------------------------------------------


def test_evaluate_extended_returns_present_yogas():
    context = _ctx(planet_houses={"sun": 1, "mercury": 1, "jupiter": 4, "venus": 1})
    results = evaluate_extended_yogas(context)
    # At least Budha-Aditya (Strong) should be present
    names = [r.name for r in results]
    assert "Budha-Aditya (Strong)" in names


def test_evaluate_extended_empty_context_returns_list():
    context = _ctx()
    results = evaluate_extended_yogas(context)
    assert isinstance(results, list)
