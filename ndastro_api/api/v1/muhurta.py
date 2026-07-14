"""Muhurta API endpoints — auspicious timing windows."""

from __future__ import annotations

import contextlib
from datetime import date, datetime, timedelta, timezone
from typing import Annotated, cast

import pytz
from fastapi import APIRouter, HTTPException, Query
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.core import get_sunrise_sunset
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.utils.chart_helpers import nakshatra_num
from ndastro_api.services.muhurta_advanced import (
    get_amrita_kala_windows,
    get_durmuhurtas,
    get_varjyam_windows,
)
from ndastro_api.core.models.muhurta import (
    AuspiciousDateResult,
    HoraWindow,
    LagnaWindow,
    TaraResult,
    TimeWindowSummary,
)
from ndastro_api.services.muhurta_range import (
    EventType,
    search_auspicious_dates,
)
from ndastro_api.services.panchanga import (
    get_tithi_number,
    get_vara_number_from_weekday,
)
from ndastro_api.services.position import get_sidereal_planet_positions

router = APIRouter(prefix="/muhurta", tags=["Timing & Predictions"], dependencies=get_conditional_dependencies())

_DEFAULT_DT = datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=pytz.utc)


class TimeWindowResponse(BaseModel):
    """A time window with start, end, and duration."""

    start: str
    end: str
    duration_minutes: float


class DurmuhurtaResponse(BaseModel):
    """An inauspicious Durmuhurta period."""

    window: TimeWindowResponse
    muhurta_index: int
    description: str


class VarjyamResponse(BaseModel):
    """A Varjyam (inauspicious) period based on tithi and nakshatra."""

    window: TimeWindowResponse
    tithi: int
    nakshatra: int
    description: str


class AmritaKalaResponse(BaseModel):
    """An Amrita Kala or Kala window based on weekday and nakshatra."""

    window: TimeWindowResponse
    quality: str
    weekday: int
    nakshatra: int
    description: str


class MuhurtaResponse(BaseModel):
    """Full muhurta analysis with all timing windows."""

    date: str
    sunrise: str | None
    sunset: str | None
    tithi: int
    nakshatra: int
    vara: int
    durmuhurtas: list[DurmuhurtaResponse]
    varjyam_windows: list[VarjyamResponse]
    amrita_kala: list[AmritaKalaResponse]
    kala_windows: list[AmritaKalaResponse]


class TimeWindowSummaryResponse(BaseModel):
    """Compact time window for auspicious range results."""

    name: str
    start: str
    end: str
    duration_minutes: float


class HoraWindowResponse(BaseModel):
    """A single planetary hora slot."""

    hora_number: int
    lord_code: str
    lord_name: str
    start: str
    end: str
    duration_minutes: float


class LagnaWindowResponse(BaseModel):
    """A contiguous window where the ascendant is in one rashi."""

    sign_number: int
    sign_name: str
    is_favorable: bool
    start: str
    end: str
    duration_minutes: float


class TaraResultResponse(BaseModel):
    """Tara Bala result from Janma Nakshatra."""

    tara_number: int
    tara_name: str
    is_auspicious: bool
    description: str


class AuspiciousDateResponse(BaseModel):
    """Scored auspiciousness details for a single date."""

    date: str
    event: str
    score: float
    tithi_number: int
    tithi_name: str
    paksha: str
    vara_number: int
    vara_name: str
    nakshatra: int
    moon_rashi: int
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
    amrita_kala: list[TimeWindowSummaryResponse]
    favorable_horas: list[HoraWindowResponse]
    tara_bala: TaraResultResponse | None
    chandra_ashtama: bool | None
    chandra_ashtama_house: int | None
    jupiter_combust: bool
    venus_combust: bool
    disha_shool_direction: str | None
    disha_shool_conflict: bool | None
    moon_body_part: str | None
    lagna_windows: list[LagnaWindowResponse]  # populated only for single-day queries
    abhijit_muhurta: TimeWindowSummaryResponse | None
    rahu_kalam: TimeWindowSummaryResponse | None
    yamagandam: TimeWindowSummaryResponse | None
    gulika: TimeWindowSummaryResponse | None
    sunrise: str | None
    sunset: str | None


class AuspiciousRangeResponse(BaseModel):
    """Auspicious date search results for a date range and event type."""

    event: str
    start_date: str
    end_date: str
    total_found: int
    results: list[AuspiciousDateResponse]


def _window_resp(w: object) -> TimeWindowResponse:
    """Convert a TimeWindow dataclass to TimeWindowResponse."""
    start = getattr(w, "start", None)
    end = getattr(w, "end", None)
    return TimeWindowResponse(
        start=start.isoformat() if start is not None and hasattr(start, "isoformat") else str(start),
        end=end.isoformat() if end is not None and hasattr(end, "isoformat") else str(end),
        duration_minutes=getattr(w, "duration_minutes", 0.0),
    )


@router.get("", response_model=MuhurtaResponse)
def get_muhurta(
    lat: Annotated[float, Query(description="Geographic latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Geographic longitude")] = 77.593611,
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = _DEFAULT_DT,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
) -> MuhurtaResponse:
    """Compute Muhurta (auspicious timing) windows for a given date and location.

    Returns Durmuhurta (inauspicious periods), Varjyam windows based on
    tithi/nakshatra, and Amrita/Kala windows based on weekday/nakshatra.
    """
    dt = _parse_dt(dateandtime)
    ayan = get_ayanamsa(dt, ayanamsa)

    planets = get_sidereal_planet_positions(lat, lon, dt, ayan)
    sun = next((p for p in planets if p.code == "SU"), None)
    moon = next((p for p in planets if p.code == "MO"), None)

    sun_lon = sun.longitude if sun else 0.0
    moon_lon = moon.longitude if moon else 0.0
    moon_nak = nakshatra_num(moon) if moon else 1

    # Sunrise and sunset
    sr: datetime | None = None
    ss: datetime | None = None
    with contextlib.suppress(Exception):
        sr, ss = get_sunrise_sunset(lat, lon, dt)

    # Panchanga elements
    tithi_num = get_tithi_number(sun_lon, moon_lon)
    vara_num = get_vara_number_from_weekday(dt.weekday())

    # Approximate tithi end time
    # Moon moves ~12.2°/day relative to Sun; remaining = (tithi_num * 12) - current_phase
    phase = (moon_lon - sun_lon) % 360.0
    current_phase = phase
    tithi_end_phase = tithi_num * 12.0
    remaining_deg = (tithi_end_phase - current_phase) % 12.0
    remaining_hours = remaining_deg / 12.2 * 24.0
    tithi_end_time = dt + timedelta(hours=remaining_hours)

    durmuhurtas = []
    if sr:
        with contextlib.suppress(Exception):
            raw = get_durmuhurtas(sr)
            durmuhurtas = [
                DurmuhurtaResponse(
                    window=_window_resp(d.window),
                    muhurta_index=d.muhurta_index,
                    description=d.description,
                )
                for d in raw
            ]

    varjyam = []
    with contextlib.suppress(Exception):
        raw_v = get_varjyam_windows(tithi_num, moon_nak, tithi_end_time)
        varjyam = [
            VarjyamResponse(
                window=_window_resp(v.window),
                tithi=v.tithi,
                nakshatra=v.nakshatra,
                description=v.description,
            )
            for v in raw_v
        ]

    amrita_list: list[AmritaKalaResponse] = []
    kala_list: list[AmritaKalaResponse] = []
    if sr and ss:
        with contextlib.suppress(Exception):
            amrita_raw, kala_raw = get_amrita_kala_windows(vara_num, moon_nak, sr, ss)
            amrita_list = [
                AmritaKalaResponse(
                    window=_window_resp(a.window),
                    quality=a.quality,
                    weekday=a.weekday,
                    nakshatra=a.nakshatra,
                    description=a.description,
                )
                for a in amrita_raw
            ]
            kala_list = [
                AmritaKalaResponse(
                    window=_window_resp(k.window),
                    quality=k.quality,
                    weekday=k.weekday,
                    nakshatra=k.nakshatra,
                    description=k.description,
                )
                for k in kala_raw
            ]

    return MuhurtaResponse(
        date=dt.date().isoformat(),
        sunrise=sr.isoformat() if sr else None,
        sunset=ss.isoformat() if ss else None,
        tithi=tithi_num,
        nakshatra=moon_nak,
        vara=vara_num,
        durmuhurtas=durmuhurtas,
        varjyam_windows=varjyam,
        amrita_kala=amrita_list,
        kala_windows=kala_list,
    )


def _tw_resp(tw: TimeWindowSummary | None) -> TimeWindowSummaryResponse | None:
    if tw is None:
        return None
    return TimeWindowSummaryResponse(
        name=tw.name, start=tw.start, end=tw.end, duration_minutes=tw.duration_minutes
    )


def _tw_resp_nn(tw: TimeWindowSummary) -> TimeWindowSummaryResponse:
    return TimeWindowSummaryResponse(name=tw.name, start=tw.start, end=tw.end, duration_minutes=tw.duration_minutes)


def _hora_resp(h: HoraWindow) -> HoraWindowResponse:
    return HoraWindowResponse(
        hora_number=h.hora_number, lord_code=h.lord_code, lord_name=h.lord_name,
        start=h.start, end=h.end, duration_minutes=h.duration_minutes,
    )


def _lagna_resp(lw: LagnaWindow) -> LagnaWindowResponse:
    return LagnaWindowResponse(
        sign_number=lw.sign_number, sign_name=lw.sign_name, is_favorable=lw.is_favorable,
        start=lw.start, end=lw.end, duration_minutes=lw.duration_minutes,
    )


def _tara_resp(t: TaraResult | None) -> TaraResultResponse | None:
    if t is None:
        return None
    return TaraResultResponse(
        tara_number=t.tara_number, tara_name=t.tara_name,
        is_auspicious=t.is_auspicious, description=t.description,
    )


def _date_resp(r: AuspiciousDateResult) -> AuspiciousDateResponse:
    return AuspiciousDateResponse(
        date=r.date,
        event=r.event,
        score=r.score,
        tithi_number=r.tithi_number,
        tithi_name=r.tithi_name,
        paksha=r.paksha,
        vara_number=r.vara_number,
        vara_name=r.vara_name,
        nakshatra=r.nakshatra,
        moon_rashi=r.moon_rashi,
        yoga_name=r.yoga_name,
        yoga_number=r.yoga_number,
        muhurta_rating=r.muhurta_rating,
        tithi_support=r.tithi_support,
        karana_support=r.karana_support,
        vara_support=r.vara_support,
        yoga_support=r.yoga_support,
        inauspicious_flags=r.inauspicious_flags,
        supporting_reasons=r.supporting_reasons,
        caution_reasons=r.caution_reasons,
        amrita_kala=[_tw_resp_nn(tw) for tw in r.amrita_kala],
        favorable_horas=[_hora_resp(h) for h in r.favorable_horas],
        tara_bala=_tara_resp(r.tara_bala),
        chandra_ashtama=r.chandra_ashtama,
        chandra_ashtama_house=r.chandra_ashtama_house,
        jupiter_combust=r.jupiter_combust,
        venus_combust=r.venus_combust,
        disha_shool_direction=r.disha_shool_direction,
        disha_shool_conflict=r.disha_shool_conflict,
        moon_body_part=r.moon_body_part,
        lagna_windows=[_lagna_resp(lw) for lw in r.lagna_windows],
        abhijit_muhurta=_tw_resp(r.abhijit_muhurta),
        rahu_kalam=_tw_resp(r.rahu_kalam),
        yamagandam=_tw_resp(r.yamagandam),
        gulika=_tw_resp(r.gulika),
        sunrise=r.sunrise,
        sunset=r.sunset,
    )


@router.get("/auspicious-range", response_model=AuspiciousRangeResponse)
def get_auspicious_muhurta_range(
    start_date: Annotated[str, Query(description="Start date in YYYY-MM-DD format", example="2026-08-01")],
    end_date: Annotated[str, Query(description="End date in YYYY-MM-DD format (max 365 days from start)", example="2026-12-31")],
    event: Annotated[EventType, Query(description="Life event type to find auspicious dates for")],
    lat: Annotated[float, Query(description="Geographic latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Geographic longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    min_score: Annotated[float | None, Query(description="Minimum auspiciousness score (0–16.5); omit to return all dates sorted by score", ge=0)] = None,
    limit: Annotated[int, Query(description="Maximum results to return", ge=1, le=100)] = 30,
    janma_nakshatra: Annotated[int | None, Query(description="Birth nakshatra number 1–27 — enables Tara Bala check", ge=1, le=27)] = None,
    birth_rashi: Annotated[int | None, Query(description="Birth Rashi 1-12 (Aries=1, Pisces=12) — enables Chandra Ashtama check", ge=1, le=12)] = None,
    travel_direction: Annotated[str | None, Query(description="Intended travel direction (north/south/east/west) — enables Disha Shool check")] = None,
    surgery_body_part: Annotated[str | None, Query(description="Body part being operated (head/neck/arms/chest/heart/abdomen/kidneys/reproductive/thighs/knees/calves/feet) — enables Moon body-part caution")] = None,
) -> AuspiciousRangeResponse:
    """Find auspicious dates within a date range for a specific life event.

    Scores each day using Vedic muhurta rules — tithi (lunar day), vara (weekday),
    nakshatra (lunar mansion), yoga, and paksha (lunar phase). Higher score = more
    auspicious. Results are sorted best-first.

    Score components (max ~16.5):
    - Base muhurta rating from panchanga data (0-10)
    - +2 for auspicious tithi, -2 for inauspicious tithi
    - +2 for auspicious vara, -2 for inauspicious vara
    - +2 for auspicious nakshatra
    - +0.5 for Shukla Paksha (waxing Moon)
    """
    try:
        sd = date.fromisoformat(start_date)
        ed = date.fromisoformat(end_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"message": f"Invalid date format: {exc}. Use YYYY-MM-DD."}) from exc

    try:
        results = search_auspicious_dates(
            start_date=sd,
            end_date=ed,
            lat=lat,
            lon=lon,
            ayanamsa_system=cast(AyanamsaSystem, ayanamsa),
            event=event,
            min_score=min_score,
            limit=limit,
            janma_nakshatra=janma_nakshatra,
            birth_rashi=birth_rashi,
            travel_direction=travel_direction,
            surgery_body_part=surgery_body_part,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc

    return AuspiciousRangeResponse(
        event=event.value,
        start_date=start_date,
        end_date=end_date,
        total_found=len(results),
        results=[_date_resp(r) for r in results],
    )
