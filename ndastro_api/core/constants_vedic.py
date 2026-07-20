"""Classical Vedic astrological constants.

These encode immutable rules from Jyotish shastra — planetary exaltation,
debilitation, own signs, natural friendships/enmities, nakshatra lords, and
classical house groupings.

All keys and values use the canonical engine type aliases:
  PlanetCode   — "SU" | "MO" | "MA" | "ME" | "JU" | "VE" | "SA" | "RA" | "KE"
  RasiCode     — "R01" (Aries) … "R12" (Pisces)
  NakshatraCode— "N01" (Ashwini) … "N27" (Revati)
  HouseCode    — "H01" … "H12"
"""

from __future__ import annotations

from ndastro_engine.enums import HouseCode, NakshatraCode, PlanetCode, RasiCode

# ---------------------------------------------------------------------------
# Exaltation signs — RasiCode of maximum strength
# ---------------------------------------------------------------------------

PLANET_EXALTATION: dict[PlanetCode, RasiCode] = {
    "SU": "R01",   # Sun exalted in Aries
    "MO": "R02",   # Moon exalted in Taurus
    "MA": "R10",   # Mars exalted in Capricorn
    "ME": "R06",   # Mercury exalted in Virgo
    "JU": "R04",   # Jupiter exalted in Cancer
    "VE": "R12",   # Venus exalted in Pisces
    "SA": "R07",   # Saturn exalted in Libra
    "RA": "R02",   # Rahu exalted in Taurus (traditional)
    "KE": "R08",   # Ketu exalted in Scorpio (traditional)
}

# ---------------------------------------------------------------------------
# Debilitation signs — RasiCode of minimum strength (opposite of exaltation)
# ---------------------------------------------------------------------------

PLANET_DEBILITATION: dict[PlanetCode, RasiCode] = {
    "SU": "R07",   # Libra
    "MO": "R08",   # Scorpio
    "MA": "R04",   # Cancer
    "ME": "R12",   # Pisces
    "JU": "R10",   # Capricorn
    "VE": "R06",   # Virgo
    "SA": "R01",   # Aries
}

# ---------------------------------------------------------------------------
# Own signs — list of RasiCode ruled by each planet
# ---------------------------------------------------------------------------

PLANET_OWN_SIGNS: dict[PlanetCode, list[RasiCode]] = {
    "SU": ["R05"],            # Leo
    "MO": ["R04"],            # Cancer
    "MA": ["R01", "R08"],     # Aries, Scorpio
    "ME": ["R03", "R06"],     # Gemini, Virgo
    "JU": ["R09", "R12"],     # Sagittarius, Pisces
    "VE": ["R02", "R07"],     # Taurus, Libra
    "SA": ["R10", "R11"],     # Capricorn, Aquarius
}

# ---------------------------------------------------------------------------
# Natural planetary friendships and enmities
# ---------------------------------------------------------------------------

PLANET_NATURAL_FRIENDS: dict[PlanetCode, list[PlanetCode]] = {
    "SU": ["MO", "MA", "JU"],
    "MO": ["SU", "ME"],
    "MA": ["SU", "MO", "JU"],
    "ME": ["SU", "VE"],
    "JU": ["SU", "MO", "MA"],
    "VE": ["ME", "SA"],
    "SA": ["ME", "VE"],
    "RA": ["ME", "VE", "SA"],
    "KE": ["MA", "JU", "SA"],
}

PLANET_NATURAL_ENEMIES: dict[PlanetCode, list[PlanetCode]] = {
    "SU": ["VE", "SA"],
    "MO": ["RA", "KE"],
    "MA": ["ME"],
    "ME": ["MO"],
    "JU": ["ME", "VE"],
    "VE": ["SU", "MO"],
    "SA": ["SU", "MO", "MA"],
    "RA": ["SU", "MO"],
    "KE": ["VE", "ME"],
}

# ---------------------------------------------------------------------------
# Nakshatra lords — NakshatraCode → ruling PlanetCode
# Sequence: KE VE SU MO MA RA JU SA ME  ×3 for all 27 nakshatras
# ---------------------------------------------------------------------------

NAKSHATRA_LORDS: dict[NakshatraCode, PlanetCode] = {
    "N01": "KE", "N02": "VE", "N03": "SU", "N04": "MO", "N05": "MA",
    "N06": "RA", "N07": "JU", "N08": "SA", "N09": "ME",
    "N10": "KE", "N11": "VE", "N12": "SU", "N13": "MO", "N14": "MA",
    "N15": "RA", "N16": "JU", "N17": "SA", "N18": "ME",
    "N19": "KE", "N20": "VE", "N21": "SU", "N22": "MO", "N23": "MA",
    "N24": "RA", "N25": "JU", "N26": "SA", "N27": "ME",
}

# ---------------------------------------------------------------------------
# Classical house groupings — HouseCode sets
# ---------------------------------------------------------------------------

KENDRA_HOUSES: frozenset[HouseCode] = frozenset({"H01", "H04", "H07", "H10"})
TRIKONA_HOUSES: frozenset[HouseCode] = frozenset({"H01", "H05", "H09"})
DUSTHANA_HOUSES: frozenset[HouseCode] = frozenset({"H06", "H08", "H12"})
UPACHAYA_HOUSES: frozenset[HouseCode] = frozenset({"H03", "H06", "H10", "H11"})
MARAKA_HOUSES: frozenset[HouseCode] = frozenset({"H02", "H07"})

