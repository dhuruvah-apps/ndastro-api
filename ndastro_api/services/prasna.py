"""Prasna Shastra (Vedic Horary Astrology) — query topic analysis service.

Given the moment a person arrives (lat/lon/time), the service analyses the
Lagna, Moon, 7th lord, and strongest planet to predict the topic of their
unspoken question using classical Prasna rules.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import cast

from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.enums import Houses, Nakshatras, Planets, Rasis, PlanetCode
from ndastro_engine.constants import TOTAL_NAKSHATRAS, TOTAL_RASI

from ndastro_api.core.constants_prasna import HOUSE_TOPICS as _HOUSE_TOPICS
from ndastro_api.services.position import get_sidereal_planet_positions
from ndastro_api.core.constants_vedic import (
    KENDRA_HOUSES,
    PLANET_DEBILITATION,
    PLANET_EXALTATION,
    PLANET_NATURAL_ENEMIES,
    PLANET_NATURAL_FRIENDS,
    PLANET_OWN_SIGNS,
)
from ndastro_api.core.models.prasna import PrasnaChartSnapshot, PrasnaResult, PrasnaTopicResult



# ---------------------------------------------------------------------------
# Vedic constants — derived from engine enums where possible
# ---------------------------------------------------------------------------

# Sign names (0-indexed) — derived from Rasis enum (engine is canonical source)
_SIGN_NAMES: list[str] = [Rasis(i + 1).name.title() for i in range(TOTAL_RASI)]

# Sign index 0-11 → ruling planet code — derived from Rasis.owner (no duplication)
# owner is typed Planets | None but is never None for the 12 signs; guarded below.
_SIGN_LORDS: dict[int, PlanetCode] = {
    i: owner.code
    for i in range(TOTAL_RASI)
    if (owner := Rasis(i + 1).owner) is not None
}

# Nakshatra lords — positional list derived directly from Nakshatras.owner
# (same as constants_vedic.NAKSHATRA_LORDS but as a fast 0-indexed accessor)
_NAKSHATRA_LORDS: list[PlanetCode] = [Nakshatras(i + 1).owner.code for i in range(TOTAL_NAKSHATRAS)]

# Nakshatra display names — derived from Nakshatras enum (engine is canonical source)
# Engine uses Tamil transliterations: Aswinni, Kaarthikai, Roghini, Mirugasirisam…
_NAKSHATRA_NAMES: list[str] = [Nakshatras(i + 1).name.title() for i in range(TOTAL_NAKSHATRAS)]

# Planet display names (full) — derived from Planets enum
# Note: engine uses Tamil spelling "Kethu"; Sanskrit is "Ketu".
_PLANET_FULL_NAMES: dict[str, str] = {
    p.code: p.name.title()
    for p in Planets
    if p not in (Planets.EMPTY, Planets.ASCENDANT)
}

# Fast lookup set of planet codes for filtering position-service results (9 grahas only)
_PRASNA_CODES: frozenset[str] = frozenset(
    p.code for p in Planets if p not in (Planets.EMPTY, Planets.ASCENDANT)
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyse_prasna_query(
    lat: float,
    lon: float,
    dt: datetime,
    ayanamsa_system: AyanamsaSystem = "lahiri",
) -> PrasnaResult:
    """Analyse the Prasna chart at the given moment and predict the query topic.

    Args:
        lat: Geographic latitude of the questioner.
        lon: Geographic longitude of the questioner.
        dt: Timezone-aware datetime of the query (defaults to UTC now if naive).
        ayanamsa_system: Ayanamsa to use (default 'lahiri').

    Returns:
        PrasnaResult with chart snapshot and top-3 ranked topic predictions.

    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    ayan = get_ayanamsa(dt, ayanamsa_system)

    # --- All planet data via the position service (single ephemeris call) ---
    planet_list = get_sidereal_planet_positions(lat, lon, dt, ayan)

    # --- Lagna from ascendant in planet list ---
    asc_planet = next((p for p in planet_list if p.is_ascendant), None)
    sid_asc = asc_planet.longitude if asc_planet else 0.0
    lagna_sign = _sign(sid_asc)

    # --- Sidereal longitudes for the 9 Prasna planets ---
    planet_lons: dict[PlanetCode, float] = {
        p.code: p.longitude for p in planet_list if p.code in _PRASNA_CODES
    }

    # --- House assignments (whole-sign from Lagna) ---
    planet_houses: dict[PlanetCode, int] = {
        code: _house(lon, lagna_sign) for code, lon in planet_lons.items()
    }

    # --- Moon nakshatra (reused from planet data) ---
    moon_planet = next((p for p in planet_list if p.code == Planets.MOON.code), None)
    moon_lon = planet_lons.get(Planets.MOON.code, 0.0)
    moon_sign = _sign(moon_lon)
    if moon_planet and moon_planet.nakshatra:
        moon_nak_index = int(moon_planet.nakshatra[1:]) - 1   # "N05" → 4 (0-based)
        moon_nak_number = int(moon_planet.nakshatra[1:])       # 1-27
    else:
        moon_nak_index = int(moon_lon / (360 / 27))
        moon_nak_number = moon_nak_index + 1
    moon_nak_lord = _NAKSHATRA_LORDS[moon_nak_index]
    moon_nak_name = _NAKSHATRA_NAMES[moon_nak_index]
    moon_house = planet_houses.get(Planets.MOON.code, 1)

    # --- Lagna lord & 7th lord ---
    lagna_lord = _SIGN_LORDS[lagna_sign]
    lagna_lord_house = planet_houses.get(lagna_lord, 1)
    seventh_sign = (lagna_sign + 6) % 12
    seventh_lord = _SIGN_LORDS[seventh_sign]
    seventh_lord_house = planet_houses.get(seventh_lord, 7)

    # --- Planet strengths ---
    planet_strengths: dict[PlanetCode, float] = {
        code: _planet_strength(code, _sign(lon))
        for code, lon in planet_lons.items()
    }
    strongest_planet = cast(PlanetCode, max(planet_strengths, key=lambda c: planet_strengths[c], default=Planets.JUPITER.code))
    strongest_planet_house = planet_houses.get(strongest_planet, 1)
    strongest_planet_sign = _sign(planet_lons.get(strongest_planet, 0.0))

    # --- House occupancy count ---
    house_counts: dict[int, int] = defaultdict(int)
    for h in planet_houses.values():
        house_counts[h] += 1

    # --- Score houses ---
    scores: dict[int, float] = defaultdict(float)

    scores[moon_house] += 3.0                              # R1: Moon's mind
    scores[seventh_lord_house] += 2.0                      # R2: 7th lord
    scores[lagna_lord_house] += 2.0                        # R3: Lagna lord
    for h, count in house_counts.items():                  # R4: Occupied houses
        if count >= 2:
            scores[h] += count * 0.7
    scores[strongest_planet_house] += 1.5                  # R5: Strongest planet
    if moon_nak_lord in planet_houses:
        scores[planet_houses[moon_nak_lord]] += 1.0        # R6: Nakshatra lord
    for house in (Houses.from_code(h).value for h in KENDRA_HOUSES):  # R7: Kendra boost
        if house_counts[house] > 0:
            scores[house] += 0.3 * house_counts[house]

    # Normalise to 0-1
    max_score = max(scores.values(), default=1.0)
    if max_score == 0:
        max_score = 1.0
    normalised: dict[int, float] = {h: s / max_score for h, s in scores.items()}

    # Top-3 houses (1-indexed)
    top_houses = sorted(normalised.keys(), key=lambda h: normalised[h], reverse=True)[:3]

    # --- Build topic results ---
    topic_results: list[PrasnaTopicResult] = []
    for rank, house in enumerate(top_houses, start=1):
        confidence = round(normalised[house], 2)
        indicator = _primary_indicator(
            house, moon_house, lagna_lord, lagna_lord_house,
            seventh_lord, seventh_lord_house, strongest_planet,
            strongest_planet_house, moon_nak_lord,
        )
        paragraph = _build_paragraph(
            rank=rank,
            house=house,
            lagna_sign=lagna_sign,
            lagna_lord=lagna_lord,
            lagna_lord_house=lagna_lord_house,
            moon_sign=moon_sign,
            moon_house=moon_house,
            moon_nak_name=moon_nak_name,
            moon_nak_lord=moon_nak_lord,
            seventh_lord=seventh_lord,
            seventh_lord_house=seventh_lord_house,
            strongest_planet=strongest_planet,
            strongest_planet_house=strongest_planet_house,
            strongest_planet_sign=strongest_planet_sign,
            planet_houses=planet_houses,
            house_counts=house_counts,
            indicator=indicator,
            confidence=confidence,
        )
        label, _, _ = _HOUSE_TOPICS.get(Houses(house), ("Unknown", "", ""))
        topic_results.append(PrasnaTopicResult(
            rank=rank,
            topic=label,
            confidence=confidence,
            primary_house=house,
            primary_indicator=indicator,
            paragraph=paragraph,
        ))

    chart = PrasnaChartSnapshot(
        lagna_sign_number=lagna_sign + 1,
        lagna_sign_name=_SIGN_NAMES[lagna_sign],
        lagna_lord_code=lagna_lord,
        lagna_lord_house=lagna_lord_house,
        moon_sign_number=moon_sign + 1,
        moon_sign_name=_SIGN_NAMES[moon_sign],
        moon_house=moon_house,
        moon_nakshatra_number=moon_nak_number,
        moon_nakshatra_name=moon_nak_name,
        moon_nakshatra_lord_code=moon_nak_lord,
        seventh_lord_code=seventh_lord,
        seventh_lord_house=seventh_lord_house,
        strongest_planet_code=strongest_planet,
        strongest_planet_house=strongest_planet_house,
        strongest_planet_sign_name=_SIGN_NAMES[strongest_planet_sign],
    )

    return PrasnaResult(
        datetime_utc=dt.astimezone(UTC).isoformat(timespec="seconds"),
        chart=chart,
        topics=tuple(topic_results),
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _rasi_to_idx(code: str) -> int:
    """Convert RasiCode ('R01'…'R12') to 0-indexed sign (0–11)."""
    return int(code[1:]) - 1


def _sign(longitude: float) -> int:
    """Return 0-indexed sign (0=Aries … 11=Pisces) from sidereal longitude."""
    return int(longitude / 30) % 12


def _house(planet_lon: float, lagna_sign: int) -> int:
    """Whole-sign house (1-12) of a planet relative to lagna."""
    planet_sign = _sign(planet_lon)
    return (planet_sign - lagna_sign) % 12 + 1


def _planet_strength(code: PlanetCode, sign: int) -> float:
    """Simplified dignity strength (0.25–3.0)."""
    exalt = PLANET_EXALTATION.get(code)
    if exalt is not None and sign == _rasi_to_idx(exalt):
        return 3.0
    own = PLANET_OWN_SIGNS.get(code, [])
    if any(sign == _rasi_to_idx(r) for r in own):
        return 2.5
    debit = PLANET_DEBILITATION.get(code)
    if debit is not None and sign == _rasi_to_idx(debit):
        return 0.25
    lord = _SIGN_LORDS[sign]
    if lord in PLANET_NATURAL_FRIENDS.get(code, []):
        return 2.0
    if lord in PLANET_NATURAL_ENEMIES.get(code, []):
        return 0.8
    return 1.5   # neutral sign


def _ord(n: int) -> str:
    """1 → '1st', 7 → '7th', etc."""
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th")
    return f"{n}{suffix}"


def _primary_indicator(
    house: int,
    moon_house: int,
    lagna_lord: str,
    lagna_lord_house: int,
    seventh_lord: str,
    seventh_lord_house: int,
    strongest_planet: str,
    strongest_planet_house: int,
    moon_nak_lord: str,
) -> str:
    if house == moon_house:
        return f"Moon occupies the {_ord(house)} house"
    if house == seventh_lord_house:
        return f"{_PLANET_FULL_NAMES[seventh_lord]}, lord of the 7th, is placed in the {_ord(house)} house"
    if house == lagna_lord_house:
        return f"{_PLANET_FULL_NAMES[lagna_lord]}, lord of Lagna, is placed in the {_ord(house)} house"
    if house == strongest_planet_house:
        return f"{_PLANET_FULL_NAMES[strongest_planet]} is the strongest planet and occupies the {_ord(house)} house"
    return f"Multiple indicators converge on the {_ord(house)} house"


def _build_paragraph(
    *,
    rank: int,
    house: int,
    lagna_sign: int,
    lagna_lord: str,
    lagna_lord_house: int,
    moon_sign: int,
    moon_house: int,
    moon_nak_name: str,
    moon_nak_lord: str,
    seventh_lord: str,
    seventh_lord_house: int,
    strongest_planet: str,
    strongest_planet_house: int,
    strongest_planet_sign: int,
    planet_houses: dict[PlanetCode, int],
    house_counts: dict[int, int],
    indicator: str,
    confidence: float,
) -> str:
    _, single_phrase, detailed_desc = _HOUSE_TOPICS.get(
        Houses(house), ("Unknown", "something unclear", "The indicators are scattered and unclear.")
    )
    lagna_name = _SIGN_NAMES[lagna_sign]
    ll_name = _PLANET_FULL_NAMES[lagna_lord]
    sl_name = _PLANET_FULL_NAMES[seventh_lord]
    sp_name = _PLANET_FULL_NAMES[strongest_planet]
    moon_sign_name = _SIGN_NAMES[moon_sign]
    sp_sign_name = _SIGN_NAMES[strongest_planet_sign]

    lines: list[str] = []

    # Opening — lagna
    lines.append(
        f"At the moment of this query, {lagna_name} rises as the Lagna "
        f"with {ll_name} as its lord, now placed in the {_ord(lagna_lord_house)} house."
    )

    # Moon — mind of the questioner
    lines.append(
        f"The Moon — representing the mind and its preoccupations — occupies {moon_sign_name} "
        f"in the {_ord(moon_house)} house, within the nakshatra {moon_nak_name} "
        f"whose lord is {_PLANET_FULL_NAMES[moon_nak_lord]}."
    )

    # 7th lord — classical "what you came about"
    lines.append(
        f"Classically, the 7th lord ({sl_name}) reveals what the questioner came about; "
        f"here it resides in the {_ord(seventh_lord_house)} house."
    )

    # Strongest planet
    lines.append(
        f"The strongest planet in this chart is {sp_name} in {sp_sign_name} "
        f"(the {_ord(strongest_planet_house)} house), lending its significations considerable weight."
    )

    # Occupied houses note
    busy = sorted(
        [h for h, c in house_counts.items() if c >= 2],
        key=lambda h: house_counts[h],
        reverse=True,
    )
    if busy:
        planet_names = ", ".join(
            _PLANET_FULL_NAMES[c] for c, h in planet_houses.items() if h == busy[0]
        )
        lines.append(
            f"The {_ord(busy[0])} house is the most occupied, with {planet_names} gathered there, "
            f"intensifying its themes."
        )

    # Primary driving rule
    lines.append(f"The dominant Prasna indicator here is: {indicator}.")

    # Conclusion
    lines.append(
        f"Taken together, these classical signs point with "
        f"{'strong' if confidence >= 0.7 else 'moderate' if confidence >= 0.4 else 'some'} "
        f"conviction toward {single_phrase}. {detailed_desc}"
    )

    return " ".join(lines)
