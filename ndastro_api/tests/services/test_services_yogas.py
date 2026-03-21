"""Unit tests for ndastro_api.services.yogas."""

import pytest

from ndastro_api.services.yogas import (
    NITYA_YOGA_NAMES,
    PLANET_CODE_MAP,
    YOGA_ARC_DEGREES,
    YOGA_COUNT,
    NityaYogaResult,
    PlanetaryYogaContext,
    YogaRuleResult,
    calculate_nitya_yoga,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_yoga_count_is_27():
    assert YOGA_COUNT == 27


def test_yoga_arc_is_360_over_27():
    assert pytest.approx(360.0 / 27) == YOGA_ARC_DEGREES


def test_nitya_yoga_names_count():
    assert len(NITYA_YOGA_NAMES) == 27


def test_planet_code_map_keys():
    expected_codes = {"su", "mo", "ma", "me", "ju", "ve", "sa", "ra", "ke"}
    assert set(PLANET_CODE_MAP.keys()) == expected_codes


# ---------------------------------------------------------------------------
# calculate_nitya_yoga()
# ---------------------------------------------------------------------------


def test_nitya_yoga_result_is_dataclass():
    result = calculate_nitya_yoga(0.0, 0.0)
    assert isinstance(result, NityaYogaResult)


def test_nitya_yoga_at_zero_zero():
    """Sun=0, Moon=0 → sum=0 → first yoga (Vishkambha, index 1)."""
    result = calculate_nitya_yoga(0.0, 0.0)
    assert result.name == "Vishkambha"
    assert result.number == 1


def test_nitya_yoga_number_in_range():
    for sun in range(0, 360, 30):
        for moon in range(0, 360, 30):
            result = calculate_nitya_yoga(float(sun), float(moon))
            assert 1 <= result.number <= 27


def test_nitya_yoga_arc_boundaries():
    result = calculate_nitya_yoga(10.0, 5.0)
    assert result.arc_start < result.arc_end
    assert result.longitude_sum == pytest.approx(15.0)


def test_nitya_yoga_wraps_at_360():
    """Longitudes that sum beyond 360 should still give a valid yoga."""
    result = calculate_nitya_yoga(300.0, 80.0)  # sum = 380 → normalized 20
    assert 1 <= result.number <= 27


def test_nitya_yoga_last_yoga():
    """Sum just before 360 should be Vaidhriti (27)."""
    arc = 360.0 / 27
    # Choose a sum that falls in the 27th arc: 26 * arc + 1
    target_sum = 26 * arc + 1.0
    result = calculate_nitya_yoga(target_sum, 0.0)
    assert result.number == 27
    assert result.name == "Vaidhriti"


# ---------------------------------------------------------------------------
# PlanetaryYogaContext dataclass
# ---------------------------------------------------------------------------


def test_planetary_yoga_context_basic():
    ctx = PlanetaryYogaContext(
        planet_houses={"jupiter": 1, "venus": 5},
        planet_rasis={"jupiter": "sagittarius", "venus": "leo"},
    )
    assert ctx.planet_houses["jupiter"] == 1
    assert ctx.own_signs is None


# ---------------------------------------------------------------------------
# YogaRuleResult dataclass
# ---------------------------------------------------------------------------


def test_yoga_rule_result_fields():
    result = YogaRuleResult(
        name="Gajakesari",
        category="Raja Yoga",
        is_present=True,
        planets_involved=["jupiter", "moon"],
        details="Jupiter in kendra from Moon",
    )
    assert result.is_present is True
    assert "jupiter" in result.planets_involved
