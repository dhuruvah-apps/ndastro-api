"""Bhava (house) strength calculation utilities.

Provides a configurable scoring model for house strength based on:
- Planets occupying the house
- Lord dignity and strength
- Aspects from benefics/malefics
- Ashtakavarga points (optional)
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Constants
HOUSE_COUNT = 12
VERY_STRONG_THRESHOLD = 10.0
STRONG_THRESHOLD = 6.0
WEAK_THRESHOLD = -2.0
VERY_WEAK_THRESHOLD = -6.0

DEFAULT_BENEFICS = {"jupiter", "venus", "mercury", "moon"}
DEFAULT_MALEFICS = {"saturn", "mars", "sun", "rahu", "kethu"}

HOUSE_MEANINGS = {
    1: "Self, appearance, personality, vitality",
    2: "Wealth, family, speech, food",
    3: "Siblings, courage, communication, short journeys",
    4: "Mother, home, property, peace of mind",
    5: "Children, creativity, intellect, romance",
    6: "Enemies, debts, health issues, service",
    7: "Spouse, partnerships, business, relationships",
    8: "Longevity, inheritance, secrets, transformation",
    9: "Father, luck, philosophy, long journeys, religion",
    10: "Career, reputation, status, authority",
    11: "Income, gains, friendships, aspirations",
    12: "Losses, expenses, isolation, liberation",
}


class BhavaStrengthClass:
    """Strength class labels for bhava scoring."""

    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    VERY_WEAK = "very_weak"


@dataclass
class BhavaStrengthWeights:
    """Weights for bhava strength scoring."""

    occupant_benefic: float = 2.0
    occupant_malefic: float = -2.0
    occupant_neutral: float = 1.0
    aspect_benefic: float = 1.0
    aspect_malefic: float = -1.0
    lord_exalted: float = 3.0
    lord_own_sign: float = 2.0
    lord_debilitated: float = -3.0
    lord_strength_multiplier: float = 0.05
    ashtakavarga_multiplier: float = 0.5


@dataclass
class BhavaStrengthContext:
    """Context inputs for bhava strength calculation."""

    planet_houses: dict[str, int]
    house_lords: dict[int, str]
    planet_strengths: dict[str, float] | None = None
    benefic_planets: set[str] = field(default_factory=lambda: set(DEFAULT_BENEFICS))
    malefic_planets: set[str] = field(default_factory=lambda: set(DEFAULT_MALEFICS))
    exalted_planets: set[str] | None = None
    own_sign_planets: set[str] | None = None
    debilitated_planets: set[str] | None = None
    aspects_to_houses: dict[int, list[str]] | None = None
    ashtakavarga_points: dict[int, int] | None = None


@dataclass
class BhavaStrengthResult:
    """Result for a single bhava."""

    house: int
    score: float
    classification: str
    meaning: str
    details: list[str] = field(default_factory=list)


@dataclass
class BhavaStrengthSummary:
    """Summary of bhava strength analysis."""

    results: dict[int, BhavaStrengthResult] = field(default_factory=dict)
    strong_houses: list[int] = field(default_factory=list)
    weak_houses: list[int] = field(default_factory=list)
    average_score: float = 0.0


def _normalize_planet_key(planet: str) -> str:
    return planet.strip().lower()


def _classify_score(score: float) -> str:
    if score >= VERY_STRONG_THRESHOLD:
        return BhavaStrengthClass.VERY_STRONG
    if score >= STRONG_THRESHOLD:
        return BhavaStrengthClass.STRONG
    if score <= VERY_WEAK_THRESHOLD:
        return BhavaStrengthClass.VERY_WEAK
    if score <= WEAK_THRESHOLD:
        return BhavaStrengthClass.WEAK
    return BhavaStrengthClass.MODERATE


def _score_occupants(
    context: BhavaStrengthContext,
    house: int,
    weights: BhavaStrengthWeights,
) -> tuple[float, list[str]]:
    score = 0.0
    details: list[str] = []

    occupants = [planet for planet, value in context.planet_houses.items() if value == house]
    for planet in occupants:
        normalized = _normalize_planet_key(planet)
        if normalized in context.benefic_planets:
            score += weights.occupant_benefic
            details.append(f"Benefic occupant: {planet}")
        elif normalized in context.malefic_planets:
            score += weights.occupant_malefic
            details.append(f"Malefic occupant: {planet}")
        else:
            score += weights.occupant_neutral
            details.append(f"Neutral occupant: {planet}")

    return score, details


def _score_lord(
    context: BhavaStrengthContext,
    house: int,
    weights: BhavaStrengthWeights,
) -> tuple[float, list[str]]:
    score = 0.0
    details: list[str] = []

    lord = _normalize_planet_key(context.house_lords.get(house, ""))
    if not lord:
        return score, details

    if context.exalted_planets and lord in context.exalted_planets:
        score += weights.lord_exalted
        details.append(f"Lord exalted: {lord}")
    if context.own_sign_planets and lord in context.own_sign_planets:
        score += weights.lord_own_sign
        details.append(f"Lord in own sign: {lord}")
    if context.debilitated_planets and lord in context.debilitated_planets:
        score += weights.lord_debilitated
        details.append(f"Lord debilitated: {lord}")

    if context.planet_strengths and lord in context.planet_strengths:
        strength = context.planet_strengths[lord]
        score += strength * weights.lord_strength_multiplier
        details.append(f"Lord strength adds: {strength}")

    return score, details


def _score_aspects(
    context: BhavaStrengthContext,
    house: int,
    weights: BhavaStrengthWeights,
) -> tuple[float, list[str]]:
    score = 0.0
    details: list[str] = []

    if not context.aspects_to_houses or house not in context.aspects_to_houses:
        return score, details

    for planet in context.aspects_to_houses[house]:
        normalized = _normalize_planet_key(planet)
        if normalized in context.benefic_planets:
            score += weights.aspect_benefic
            details.append(f"Benefic aspect: {planet}")
        elif normalized in context.malefic_planets:
            score += weights.aspect_malefic
            details.append(f"Malefic aspect: {planet}")

    return score, details


def _score_ashtakavarga(
    context: BhavaStrengthContext,
    house: int,
    weights: BhavaStrengthWeights,
) -> tuple[float, list[str]]:
    score = 0.0
    details: list[str] = []

    if not context.ashtakavarga_points or house not in context.ashtakavarga_points:
        return score, details

    points = context.ashtakavarga_points[house]
    score += points * weights.ashtakavarga_multiplier
    details.append(f"Ashtakavarga points: {points}")

    return score, details


def calculate_bhava_strength(
    context: BhavaStrengthContext,
    *,
    weights: BhavaStrengthWeights | None = None,
) -> BhavaStrengthSummary:
    """Calculate bhava strength using configurable inputs.

    Args:
        context: BhavaStrengthContext with placements and optional strength inputs
        weights: BhavaStrengthWeights overrides

    Returns:
        BhavaStrengthSummary with per-house results

    """
    weights = weights or BhavaStrengthWeights()
    summary = BhavaStrengthSummary()

    for house in range(1, HOUSE_COUNT + 1):
        score = 0.0
        details: list[str] = []

        occupant_score, occupant_details = _score_occupants(context, house, weights)
        lord_score, lord_details = _score_lord(context, house, weights)
        aspect_score, aspect_details = _score_aspects(context, house, weights)
        ashtakavarga_score, ashtakavarga_details = _score_ashtakavarga(context, house, weights)

        score += occupant_score + lord_score + aspect_score + ashtakavarga_score
        details.extend(occupant_details + lord_details + aspect_details + ashtakavarga_details)

        summary.results[house] = BhavaStrengthResult(
            house=house,
            score=score,
            classification=_classify_score(score),
            meaning=HOUSE_MEANINGS.get(house, f"House {house}"),
            details=details,
        )

    scores = [result.score for result in summary.results.values()]
    summary.average_score = sum(scores) / len(scores) if scores else 0.0

    for house, result in summary.results.items():
        if result.classification in {BhavaStrengthClass.STRONG, BhavaStrengthClass.VERY_STRONG}:
            summary.strong_houses.append(house)
        if result.classification in {BhavaStrengthClass.WEAK, BhavaStrengthClass.VERY_WEAK}:
            summary.weak_houses.append(house)

    summary.strong_houses.sort()
    summary.weak_houses.sort()

    return summary


def get_bhava_strength_interpretation(result: BhavaStrengthResult) -> str:
    """Return a short interpretation for a bhava result."""
    base = f"House {result.house} ({result.meaning}): {result.score:.1f}"

    descriptions = {
        BhavaStrengthClass.VERY_STRONG: "Excellent strength",
        BhavaStrengthClass.STRONG: "Strong support",
        BhavaStrengthClass.MODERATE: "Moderate strength",
        BhavaStrengthClass.WEAK: "Weak support",
        BhavaStrengthClass.VERY_WEAK: "Highly afflicted",
    }

    return f"{base} - {descriptions.get(result.classification, 'Mixed')}"
