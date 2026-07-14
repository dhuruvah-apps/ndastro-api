"""Frozen dataclasses for muhurta (electional astrology) result types.

These are the public data-transfer objects produced by the muhurta range
service and consumed by the API layer.  They live here rather than inline
in the service so that the API, tests, and any future consumers can import
them without depending on the full service module.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeWindowSummary:
    """A labelled time window (start / end / duration)."""

    name: str
    start: str
    end: str
    duration_minutes: float


@dataclass(frozen=True)
class HoraWindow:
    """A single planetary hora (1-hour) slot with its ruling planet."""

    hora_number: int
    lord_code: str
    lord_name: str
    start: str
    end: str
    duration_minutes: float


@dataclass(frozen=True)
class LagnaWindow:
    """A contiguous window where the ascendant (Lagna) is in one rashi."""

    sign_number: int        # 1-12
    sign_name: str
    is_favorable: bool
    start: str              # ISO datetime
    end: str
    duration_minutes: float


@dataclass(frozen=True)
class TaraResult:
    """Tara Bala result — 9-star strength computed from Janma Nakshatra."""

    tara_number: int
    tara_name: str
    is_auspicious: bool
    description: str


@dataclass(frozen=True)
class AuspiciousDateResult:
    """Fully scored and enriched result for a single candidate date."""

    date: str
    event: str
    score: float
    tithi_number: int
    tithi_name: str
    paksha: str
    vara_number: int
    vara_name: str
    nakshatra: int
    yoga_name: str
    yoga_number: int
    muhurta_rating: float | None
    tithi_support: bool
    karana_support: bool
    vara_support: bool
    yoga_support: bool
    inauspicious_flags: list[str]
    supporting_reasons: list[str]
    caution_reasons: list[str]
    abhijit_muhurta: TimeWindowSummary | None
    rahu_kalam: TimeWindowSummary | None
    yamagandam: TimeWindowSummary | None
    gulika: TimeWindowSummary | None
    sunrise: str | None
    sunset: str | None
    # Fields populated lazily by _enrich_timing() after phase-1 scoring
    moon_rashi: int = 0
    amrita_kala: tuple[TimeWindowSummary, ...] = ()
    favorable_horas: tuple[HoraWindow, ...] = ()
    tara_bala: TaraResult | None = None
    chandra_ashtama: bool | None = None
    chandra_ashtama_house: int | None = None
    # Combustion flags — computed in phase-1 alongside panchanga
    jupiter_combust: bool = False
    venus_combust: bool = False
    # Disha Shool — populated during enrichment when travel_direction is supplied
    disha_shool_direction: str | None = None
    disha_shool_conflict: bool | None = None
    # Moon body-part surgery rule — populated during enrichment
    moon_body_part: str | None = None
    # Lagna windows — populated only for single-day queries (start_date == end_date)
    lagna_windows: tuple[LagnaWindow, ...] = ()
