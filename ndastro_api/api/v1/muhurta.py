"""Muhurta API endpoints — auspicious timing windows."""

from __future__ import annotations

import contextlib
from datetime import datetime, timedelta, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
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
