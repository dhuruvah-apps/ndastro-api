"""Frozen dataclasses for Prasna (Vedic horary astrology) result types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrasnaTopicResult:
    """A single ranked topic prediction from the Prasna chart."""

    rank: int
    topic: str                   # short label, e.g. "Marriage & Partnership"
    confidence: float            # 0.0 – 1.0
    primary_house: int           # 1-12 house that drives this prediction
    primary_indicator: str       # human-readable trigger, e.g. "Moon in 7th house"
    paragraph: str               # full Prasna analysis paragraph


@dataclass(frozen=True)
class PrasnaChartSnapshot:
    """Snapshot of key chart elements at the moment of query."""

    lagna_sign_number: int       # 1-12
    lagna_sign_name: str
    lagna_lord_code: str
    lagna_lord_house: int
    moon_sign_number: int
    moon_sign_name: str
    moon_house: int
    moon_nakshatra_number: int
    moon_nakshatra_name: str
    moon_nakshatra_lord_code: str
    seventh_lord_code: str
    seventh_lord_house: int
    strongest_planet_code: str
    strongest_planet_house: int
    strongest_planet_sign_name: str


@dataclass(frozen=True)
class PrasnaResult:
    """Complete Prasna reading for the moment of query."""

    datetime_utc: str
    chart: PrasnaChartSnapshot
    topics: tuple[PrasnaTopicResult, ...]   # top-3, ranked by confidence
