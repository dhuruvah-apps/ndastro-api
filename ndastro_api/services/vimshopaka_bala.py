"""Vimshopaka Bala - Composite divisional chart strength calculation.

Vimshopaka Bala aggregates a planet's dignity scores across multiple
divisional charts to produce a weighted composite strength measure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from ndastro_api.services.divisional_charts import (
    VargaType,
    compute_varga_chart,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class VimshopakaDignity(str, Enum):
    """Dignity classification for varga placement."""

    MOOLATRIKONA = "moolatrikona"
    OWN_SIGN = "own_sign"
    GREAT_FRIEND = "great_friend"
    FRIEND = "friend"
    NEUTRAL = "neutral"
    ENEMY = "enemy"
    GREAT_ENEMY = "great_enemy"
    EXALTATION = "exaltation"
    DEBILITATION = "debilitation"


# Shadvarga: 6-varga scheme (common for general analysis)
SHADVARGA_WEIGHTS = {
    VargaType.D1: 6.0,
    VargaType.D2: 2.0,
    VargaType.D3: 4.0,
    VargaType.D9: 5.0,
    VargaType.D12: 2.0,
    VargaType.D30: 1.0,
}

# Saptavarga: 7-varga scheme
SAPTAVARGA_WEIGHTS = {
    VargaType.D1: 5.0,
    VargaType.D2: 2.0,
    VargaType.D3: 3.0,
    VargaType.D7: 1.0,
    VargaType.D9: 4.5,
    VargaType.D12: 2.0,
    VargaType.D30: 1.0,
}

# Dasavarga: 10-varga scheme
DASAVARGA_WEIGHTS = {
    VargaType.D1: 3.0,
    VargaType.D2: 1.5,
    VargaType.D3: 1.5,
    VargaType.D7: 1.5,
    VargaType.D9: 3.0,
    VargaType.D10: 1.5,
    VargaType.D12: 1.5,
    VargaType.D16: 1.5,
    VargaType.D30: 1.5,
    VargaType.D60: 4.0,
}

# Shodasavarga: 16-varga scheme (comprehensive)
SHODASAVARGA_WEIGHTS = {
    VargaType.D1: 3.5,
    VargaType.D2: 1.0,
    VargaType.D3: 1.0,
    VargaType.D4: 0.5,
    VargaType.D7: 0.5,
    VargaType.D9: 3.0,
    VargaType.D10: 0.5,
    VargaType.D12: 0.5,
    VargaType.D16: 2.0,
    VargaType.D20: 0.5,
    VargaType.D24: 0.5,
    VargaType.D27: 0.5,
    VargaType.D30: 1.0,
    VargaType.D40: 0.5,
    VargaType.D45: 0.5,
    VargaType.D60: 4.0,
}

# Dignity score mapping (Virupas)
DIGNITY_SCORES = {
    VimshopakaDignity.EXALTATION: 20.0,
    VimshopakaDignity.MOOLATRIKONA: 18.0,
    VimshopakaDignity.OWN_SIGN: 15.0,
    VimshopakaDignity.GREAT_FRIEND: 12.0,
    VimshopakaDignity.FRIEND: 10.0,
    VimshopakaDignity.NEUTRAL: 7.5,
    VimshopakaDignity.ENEMY: 5.0,
    VimshopakaDignity.GREAT_ENEMY: 2.5,
    VimshopakaDignity.DEBILITATION: 2.0,
}

# Lordship and dignity definitions
EXALTATION_SIGNS = {
    "Sun": 1,
    "Moon": 2,
    "Mars": 10,
    "Mercury": 6,
    "Jupiter": 4,
    "Venus": 12,
    "Saturn": 7,
}

DEBILITATION_SIGNS = {
    "Sun": 7,
    "Moon": 8,
    "Mars": 4,
    "Mercury": 12,
    "Jupiter": 10,
    "Venus": 6,
    "Saturn": 1,
}

OWN_SIGNS = {
    "Sun": [5],
    "Moon": [4],
    "Mars": [1, 8],
    "Mercury": [3, 6],
    "Jupiter": [9, 12],
    "Venus": [2, 7],
    "Saturn": [10, 11],
}

MOOLATRIKONA_SIGNS = {
    "Sun": 5,
    "Moon": 2,
    "Mars": 1,
    "Mercury": 6,
    "Jupiter": 9,
    "Venus": 7,
    "Saturn": 11,
}

# Natural friendships (simplified matrix)
NATURAL_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
}

NATURAL_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": ["None"],
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"],
}

# Vimshopaka strength thresholds
PARIJATA_THRESHOLD = 18.0
UTTAMA_THRESHOLD = 16.0
GOPURA_THRESHOLD = 13.0
SIMHASANA_THRESHOLD = 10.0
PARAVATA_THRESHOLD = 6.0
DEVALOKA_THRESHOLD = 4.0
BHOOLOKA_THRESHOLD = 2.0


@dataclass
class VimshopakaBalaScore:
    """Vimshopaka Bala computation result for a single planet."""

    planet: str
    scheme: str
    total_weight: float
    total_score: float
    vimshopaka_ratio: float
    varga_dignities: dict[VargaType, VimshopakaDignity] = field(default_factory=dict)
    varga_scores: dict[VargaType, float] = field(default_factory=dict)
    is_parijata: bool = False
    is_uttama: bool = False
    is_gopura: bool = False
    is_simhasana: bool = False
    is_paravata: bool = False
    is_devaloka: bool = False
    is_bhooloka: bool = False
    is_naraka: bool = False


@dataclass
class VimshopakaBalaReport:
    """Vimshopaka Bala scores for all planets in a given scheme."""

    scheme: str
    max_score: float
    scores: dict[str, VimshopakaBalaScore] = field(default_factory=dict)


def _check_relationship_dignity(planet: str, sign_lord: str) -> VimshopakaDignity:
    """Check natural relationship between planet and sign lord."""
    if sign_lord in NATURAL_FRIENDS.get(planet, []):
        return VimshopakaDignity.FRIEND
    if sign_lord in NATURAL_ENEMIES.get(planet, []):
        return VimshopakaDignity.ENEMY
    return VimshopakaDignity.NEUTRAL


def get_dignity(planet: str, rasi: int) -> VimshopakaDignity:
    """Determine a planet's dignity in a sign."""
    # Check special dignities
    if planet in EXALTATION_SIGNS and EXALTATION_SIGNS[planet] == rasi:
        return VimshopakaDignity.EXALTATION
    if planet in DEBILITATION_SIGNS and DEBILITATION_SIGNS[planet] == rasi:
        return VimshopakaDignity.DEBILITATION

    # Check own sign or moolatrikona
    if planet in MOOLATRIKONA_SIGNS and MOOLATRIKONA_SIGNS[planet] == rasi:
        return VimshopakaDignity.MOOLATRIKONA
    if planet in OWN_SIGNS and rasi in OWN_SIGNS[planet]:
        return VimshopakaDignity.OWN_SIGN

    # Check relationships with sign lord
    sign_lord = _get_sign_lord(rasi)
    if sign_lord and sign_lord != planet:
        return _check_relationship_dignity(planet, sign_lord)

    return VimshopakaDignity.NEUTRAL


def _get_sign_lord(rasi: int) -> str | None:
    """Return the ruling planet of a sign."""
    lords = {
        1: "Mars",
        2: "Venus",
        3: "Mercury",
        4: "Moon",
        5: "Sun",
        6: "Mercury",
        7: "Venus",
        8: "Mars",
        9: "Jupiter",
        10: "Saturn",
        11: "Saturn",
        12: "Jupiter",
    }
    return lords.get(rasi)


def _classify_strength(ratio: float) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
    """Classify Vimshopaka strength level.

    Returns: (parijata, uttama, gopura, simhasana, paravata, devaloka, bhooloka, naraka).
    """
    thresholds = [
        (PARIJATA_THRESHOLD, (True, False, False, False, False, False, False, False)),
        (UTTAMA_THRESHOLD, (False, True, False, False, False, False, False, False)),
        (GOPURA_THRESHOLD, (False, False, True, False, False, False, False, False)),
        (SIMHASANA_THRESHOLD, (False, False, False, True, False, False, False, False)),
        (PARAVATA_THRESHOLD, (False, False, False, False, True, False, False, False)),
        (DEVALOKA_THRESHOLD, (False, False, False, False, False, True, False, False)),
        (BHOOLOKA_THRESHOLD, (False, False, False, False, False, False, True, False)),
    ]

    for threshold, flags in thresholds:
        if ratio >= threshold:
            return flags

    return (False, False, False, False, False, False, False, True)


def compute_vimshopaka_bala(
    planet_longitudes: dict[str, float],
    *,
    scheme: str = "shodasavarga",
) -> VimshopakaBalaReport:
    """Compute Vimshopaka Bala for all planets.

    Args:
        planet_longitudes: Sidereal longitudes in [0, 360).
        scheme: One of "shadvarga", "saptavarga", "dasavarga", "shodasavarga".

    Returns:
        VimshopakaBalaReport with scores for each planet.

    """
    scheme_map = {
        "shadvarga": SHADVARGA_WEIGHTS,
        "saptavarga": SAPTAVARGA_WEIGHTS,
        "dasavarga": DASAVARGA_WEIGHTS,
        "shodasavarga": SHODASAVARGA_WEIGHTS,
    }
    if scheme not in scheme_map:
        msg = f"Unknown scheme: {scheme}"
        raise ValueError(msg)

    weights = scheme_map[scheme]
    total_weight = sum(weights.values())
    max_score = DIGNITY_SCORES[VimshopakaDignity.EXALTATION]

    scores: dict[str, VimshopakaBalaScore] = {}

    for planet, longitude in planet_longitudes.items():
        varga_dignities: dict[VargaType, VimshopakaDignity] = {}
        varga_scores: dict[VargaType, float] = {}
        total_score = 0.0

        for varga_type, weight in weights.items():
            chart = compute_varga_chart(
                longitudes={planet: longitude},
                varga=varga_type,
            )
            varga_pos = chart.positions.get(planet)
            if not varga_pos:
                continue

            dignity = get_dignity(planet, varga_pos.varga_rasi)
            dignity_score = DIGNITY_SCORES[dignity]
            weighted_score = dignity_score * weight

            varga_dignities[varga_type] = dignity
            varga_scores[varga_type] = dignity_score
            total_score += weighted_score

        vimshopaka_ratio = total_score / total_weight
        (
            parijata,
            uttama,
            gopura,
            simhasana,
            paravata,
            devaloka,
            bhooloka,
            naraka,
        ) = _classify_strength(vimshopaka_ratio)

        scores[planet] = VimshopakaBalaScore(
            planet=planet,
            scheme=scheme,
            total_weight=total_weight,
            total_score=total_score,
            vimshopaka_ratio=vimshopaka_ratio,
            varga_dignities=varga_dignities,
            varga_scores=varga_scores,
            is_parijata=parijata,
            is_uttama=uttama,
            is_gopura=gopura,
            is_simhasana=simhasana,
            is_paravata=paravata,
            is_devaloka=devaloka,
            is_bhooloka=bhooloka,
            is_naraka=naraka,
        )

    return VimshopakaBalaReport(
        scheme=scheme,
        max_score=max_score,
        scores=scores,
    )


def get_strength_label(score: VimshopakaBalaScore) -> str:
    """Return a descriptive label for the strength level."""
    labels = [
        (score.is_parijata, "Parijata (Supreme)"),
        (score.is_uttama, "Uttama (Excellent)"),
        (score.is_gopura, "Gopura (Very Good)"),
        (score.is_simhasana, "Simhasana (Good)"),
        (score.is_paravata, "Paravata (Average)"),
        (score.is_devaloka, "Devaloka (Below Average)"),
        (score.is_bhooloka, "Bhooloka (Weak)"),
    ]

    for flag, label in labels:
        if flag:
            return label

    return "Naraka (Very Weak)"


def get_strongest_planets(
    report: VimshopakaBalaReport,
    *,
    top_n: int = 3,
) -> Sequence[tuple[str, float]]:
    """Return the strongest planets by Vimshopaka ratio."""
    ranked = sorted(
        report.scores.items(),
        key=lambda item: item[1].vimshopaka_ratio,
        reverse=True,
    )
    return [(planet, score.vimshopaka_ratio) for planet, score in ranked[:top_n]]
