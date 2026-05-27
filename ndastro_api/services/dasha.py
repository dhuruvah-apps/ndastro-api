"""Engine-backed dasha service.

This service is the single integration point between the API layer and
``ndastro_engine.dasa``. It exposes normalized birth info, running periods,
and timeline data with API-friendly metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from math import floor
from typing import Any, cast

from ndastro_engine.ayanamsa import AyanamsaSystem
from ndastro_engine.dasa import DasaContext
from ndastro_engine.dasa import DasaPeriod as EngineDasaPeriod
from ndastro_engine.dasa import DasaQuery, get_dasa_birth_info
from ndastro_engine.dasa import get_dasa_timeline as engine_get_dasa_timeline
from ndastro_engine.dasa import get_running_dasa as engine_get_running_dasa
from ndastro_engine.dasa import get_supported_dasa_types
from ndastro_engine.enums import NakshatraCode, Planets

from ndastro_api.core.utils.data_loader import astro_data

SECONDS_PER_YEAR = 365.25 * 24 * 3600


@dataclass(frozen=True)
class DasaBirthDetails:
    sidereal_moon_longitude: float
    janma_nakshatra_code: NakshatraCode
    janma_nakshatra_name: str
    janma_nakshatra_pada: int
    nakshatra_progress_fraction: float
    nakshatra_remaining_fraction: float
    start_lord_name: str
    start_lord_code: str


@dataclass(frozen=True)
class DasaPeriodDetails:
    dasa_type: str
    level: int
    level_name: str
    lord_name: str
    lord_code: str
    start_utc: datetime
    end_utc: datetime
    duration_years: float
    elapsed_years: float | None
    remaining_years: float | None
    progress_percent: float | None
    interpretation: str
    child_count: int
    children: tuple[DasaPeriodDetails, ...] = ()


@dataclass(frozen=True)
class RunningDasaDetails:
    dasa_type: str
    as_of_utc: datetime
    birth_info: DasaBirthDetails
    maha: DasaPeriodDetails | None
    antara: DasaPeriodDetails | None
    pratyantara: DasaPeriodDetails | None
    sookshma: DasaPeriodDetails | None


@dataclass(frozen=True)
class DasaTimelineDetails:
    dasa_type: str
    birth_info: DasaBirthDetails
    levels: int
    years: float | None
    periods: tuple[DasaPeriodDetails, ...]


def get_supported_dasa_type_names() -> tuple[str, ...]:
    """Return supported engine dasa types sorted for API output."""
    return tuple(sorted(get_supported_dasa_types()))


def normalize_dasa_type(dasa_type: str) -> str:
    """Validate and normalize a dasa type name."""
    normalized = dasa_type.strip().lower()
    supported = set(get_supported_dasa_type_names())
    if normalized not in supported:
        msg = f"Unsupported dasa type: {dasa_type!r}. Supported types: {sorted(supported)}"
        raise ValueError(msg)
    return normalized


def build_dasa_context(
    *,
    birth_datetime: datetime,
    lat: float,
    lon: float,
    ayanamsa_system: AyanamsaSystem,
    dasa_type: str,
) -> DasaContext:
    """Build a validated engine context for dasha queries."""
    return DasaContext(
        birth_datetime=birth_datetime,
        lat=lat,
        lon=lon,
        ayanamsa_system=ayanamsa_system,
        dasa_type=normalize_dasa_type(dasa_type),
    )


def get_birth_details(context: DasaContext) -> DasaBirthDetails:
    """Return normalized birth details used by all dasha responses."""
    birth_info = get_dasa_birth_info(context)
    progress_fraction = float(birth_info.nakshatra_progress_fraction)
    janma_pada = max(1, min(4, floor(progress_fraction * 4.0) + 1))
    start_lord = _planet_from_name(birth_info.start_lord)
    return DasaBirthDetails(
        sidereal_moon_longitude=float(birth_info.sidereal_moon_longitude),
        janma_nakshatra_code=birth_info.janma_nakshatra.code,
        janma_nakshatra_name=birth_info.janma_nakshatra.name,
        janma_nakshatra_pada=janma_pada,
        nakshatra_progress_fraction=progress_fraction,
        nakshatra_remaining_fraction=float(birth_info.nakshatra_remaining_fraction),
        start_lord_name=birth_info.start_lord,
        start_lord_code=start_lord.code if start_lord != Planets.EMPTY else birth_info.start_lord,
    )


def get_running_dasa_details(
    *,
    query_datetime: datetime,
    birth_datetime: datetime,
    lat: float,
    lon: float,
    ayanamsa_system: AyanamsaSystem,
    dasa_type: str,
) -> RunningDasaDetails:
    """Return current running dasa details at all supported levels."""
    context = build_dasa_context(
        birth_datetime=birth_datetime,
        lat=lat,
        lon=lon,
        ayanamsa_system=ayanamsa_system,
        dasa_type=dasa_type,
    )
    as_of_utc = _as_utc(query_datetime)
    running = engine_get_running_dasa(as_of_utc, context, DasaQuery(levels=4))
    birth_info = get_birth_details(context)

    return RunningDasaDetails(
        dasa_type=context.dasa_type,
        as_of_utc=as_of_utc,
        birth_info=birth_info,
        maha=_build_period_details(running.maha, as_of_utc=as_of_utc, include_children=False),
        antara=_build_period_details(running.antara, as_of_utc=as_of_utc, include_children=False),
        pratyantara=_build_period_details(running.pratyantara, as_of_utc=as_of_utc, include_children=False),
        sookshma=_build_period_details(running.sookshma, as_of_utc=as_of_utc, include_children=False),
    )


def get_dasa_timeline_details(
    *,
    birth_datetime: datetime,
    lat: float,
    lon: float,
    ayanamsa_system: AyanamsaSystem,
    dasa_type: str,
    levels: int,
    years: float | None,
) -> DasaTimelineDetails:
    """Return a timeline of dasa periods with optional nested lower levels."""
    context = build_dasa_context(
        birth_datetime=birth_datetime,
        lat=lat,
        lon=lon,
        ayanamsa_system=ayanamsa_system,
        dasa_type=dasa_type,
    )
    birth_info = get_birth_details(context)
    timeline = engine_get_dasa_timeline(context, DasaQuery(levels=levels, years=years))
    period_details = tuple(
        period_detail
        for period_detail in (_build_period_details(period, as_of_utc=None, include_children=levels > 1) for period in timeline)
        if period_detail is not None
    )

    return DasaTimelineDetails(
        dasa_type=context.dasa_type,
        birth_info=birth_info,
        levels=levels,
        years=years,
        periods=period_details,
    )


def _build_period_details(
    period: EngineDasaPeriod | None,
    *,
    as_of_utc: datetime | None,
    include_children: bool,
) -> DasaPeriodDetails | None:
    if period is None:
        return None

    duration_seconds = (period.end_utc - period.start_utc).total_seconds()
    elapsed_years: float | None = None
    remaining_years: float | None = None
    progress_percent: float | None = None

    if as_of_utc is not None and duration_seconds > 0:
        elapsed_seconds = min(max((as_of_utc - period.start_utc).total_seconds(), 0.0), duration_seconds)
        remaining_seconds = duration_seconds - elapsed_seconds
        elapsed_years = elapsed_seconds / SECONDS_PER_YEAR
        remaining_years = remaining_seconds / SECONDS_PER_YEAR
        progress_percent = (elapsed_seconds / duration_seconds) * 100.0

    children = ()
    if include_children:
        children = tuple(_build_period_details(child, as_of_utc=None, include_children=True) for child in period.children)
        children = tuple(child for child in children if child is not None)

    return DasaPeriodDetails(
        dasa_type=period.dasa_type,
        level=period.level,
        level_name=period.level_name,
        lord_name=period.lord,
        lord_code=_planet_from_name(period.lord).code,
        start_utc=period.start_utc,
        end_utc=period.end_utc,
        duration_years=duration_seconds / SECONDS_PER_YEAR,
        elapsed_years=elapsed_years,
        remaining_years=remaining_years,
        progress_percent=progress_percent,
        interpretation=_interpretation(period.lord, period.level_name),
        child_count=len(period.children),
        children=children,
    )


def _interpretation(lord_name: str, level_name: str) -> str:
    planet = _planet_from_name(lord_name)
    code = planet.code if planet != Planets.EMPTY else lord_name.upper()
    details = _get_vimshottari_period_details().get(code, {})
    base = _compose_interpretation_text(details)
    if not base:
        base = _get_guide_fallback_interpretation(code)
    if not base:
        base = f"{lord_name.title()} period themes"
    return f"{base} ({level_name.upper()})"


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


@lru_cache(maxsize=1)
def _get_vimshottari_period_details() -> dict[str, dict[str, str]]:
    """Load and cache Vimshottari period details from data_loader."""
    system = astro_data.get_dasha_system_by_name("Vimshottari Dasha")
    if system is None or not isinstance(system.periods, list):
        return {}

    details_by_code: dict[str, dict[str, str]] = {}
    for period in system.periods:
        planet_code = str(getattr(period, "planet", "")).upper().strip()
        if not planet_code:
            continue
        details_by_code[planet_code] = {
            "nature": str(getattr(period, "nature", "") or "").strip(),
            "effects": str(getattr(period, "effects", "") or "").strip(),
            "positive_results": str(getattr(period, "positive_results", "") or "").strip(),
        }

    return details_by_code


def _compose_interpretation_text(details: dict[str, str]) -> str:
    parts = [details.get("nature", ""), details.get("effects", "")]
    text = ". ".join(part.rstrip(".") for part in parts if part)
    if text:
        return text + "."

    positive = details.get("positive_results", "").strip()
    if positive:
        return positive.rstrip(".") + "."
    return ""


@lru_cache(maxsize=1)
def _get_guide_fallback_map() -> dict[str, str]:
    """Build a planet-name fallback map from dasha_period_guide.json."""
    guide = astro_data.get_dasha_period_guide()
    if not isinstance(guide, dict):
        return {}

    mahadashas = guide.get("mahadashas")
    if not isinstance(mahadashas, dict):
        return {}

    periods = mahadashas.get("periods")
    if not isinstance(periods, list):
        return {}

    mapping: dict[str, str] = {}
    for entry in periods:
        if not isinstance(entry, dict):
            continue
        planet = str(entry.get("planet", "")).strip().lower()
        if not planet:
            continue
        key = planet.split(" ", maxsplit=1)[0]
        planet_enum = _planet_from_name(key)
        if planet_enum == Planets.EMPTY:
            continue
        summary = _extract_guide_summary(entry)
        if summary:
            mapping[planet_enum.code] = summary
    return mapping


def _extract_guide_summary(entry: dict[str, Any]) -> str:
    """Extract a short interpretation summary from a guide entry."""
    nature = str(entry.get("nature", "") or "").strip()
    themes = entry.get("general_themes")

    parts: list[str] = []
    if nature:
        parts.append(nature.rstrip("."))
    if isinstance(themes, list):
        theme_items = [str(item).strip() for item in themes if str(item).strip()]
        if theme_items:
            parts.append(theme_items[0].rstrip("."))

    if not parts:
        return ""
    return ". ".join(parts) + "."


def _get_guide_fallback_interpretation(planet_code: str) -> str:
    return _get_guide_fallback_map().get(planet_code.upper(), "")


def _planet_from_name(name: str) -> Planets:
    """Resolve planet strings to enum using engine methods and aliases."""
    normalized = name.strip()
    if not normalized:
        return Planets.EMPTY

    enum_by_name = Planets.__members__.get(normalized.upper())
    if enum_by_name is not None:
        return enum_by_name

    aliases = {
        "ketu": "kethu",
        "mars": "mars barycenter",
        "jupiter": "jupiter barycenter",
        "saturn": "saturn barycenter",
    }
    astronomical_name = aliases.get(normalized.lower(), normalized.lower())
    return Planets.from_astronomical_code(cast("AstronomicalCode", astronomical_name))
