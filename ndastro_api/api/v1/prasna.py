"""Prasna (Vedic Horary Astrology) — query topic prediction endpoint."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
from ndastro_engine.ayanamsa import AyanamsaSystem
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.services.prasna import analyse_prasna_query

router = APIRouter(prefix="/prasna", tags=["Timing & Predictions"], dependencies=get_conditional_dependencies())

_DEFAULT_DT = datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=pytz.utc)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class PrasnaChartSnapshotResponse(BaseModel):
    """Key chart elements at the moment of query."""

    lagna_sign_number: int
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


class PrasnaTopicResponse(BaseModel):
    """A single ranked topic prediction."""

    rank: int
    topic: str
    confidence: float
    primary_house: int
    primary_indicator: str
    paragraph: str


class PrasnaResponse(BaseModel):
    """Full Prasna reading — the chart and the top-3 topic predictions."""

    datetime_utc: str
    chart: PrasnaChartSnapshotResponse
    topics: list[PrasnaTopicResponse]
    disclaimer: str = (
        "Prasna Shastra is an indicative classical system. "
        "These predictions are based on the Lagna, Moon, 7th lord, and dominant "
        "planetary positions at the moment of query. They should be interpreted "
        "by a qualified Vedic astrologer in context."
    )


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("/query-topic", response_model=PrasnaResponse, summary="Predict the topic of an unspoken query")
def get_prasna_query_topic(
    lat: Annotated[float, Query(description="Geographic latitude of the questioner", example=12.971667)],
    lon: Annotated[float, Query(description="Geographic longitude of the questioner", example=77.593611)],
    dateandtime: Annotated[str, Query(
        description="Date and time of the query in ISO format (defaults to current UTC time)",
        example=_DEFAULT_DT,
    )] = _DEFAULT_DT,
    ayanamsa: Annotated[AyanamsaSystem, Query(
        description="Ayanamsa system (default: lahiri)",
    )] = "lahiri",
) -> PrasnaResponse:
    """Analyse the Prasna chart at the exact moment of a query and reveal the likely topic.

    Based on classical Prasna Shastra rules:
    - **Moon's house** — what is on the questioner's mind
    - **7th lord's placement** — what the person came about (strongest classical rule)
    - **Lagna lord's house** — the self's primary concern
    - **Most occupied house** — where planetary energy clusters
    - **Strongest planet** — dominant life area being activated
    - **Moon's nakshatra lord** — nakshatra-level refinement

    Returns 3 ranked topic predictions, each with a full Prasna paragraph explaining
    the chart reasoning.
    """
    dt = _parse_dt(dateandtime)
    result = analyse_prasna_query(lat, lon, dt, ayanamsa)

    chart_resp = PrasnaChartSnapshotResponse(
        lagna_sign_number=result.chart.lagna_sign_number,
        lagna_sign_name=result.chart.lagna_sign_name,
        lagna_lord_code=result.chart.lagna_lord_code,
        lagna_lord_house=result.chart.lagna_lord_house,
        moon_sign_number=result.chart.moon_sign_number,
        moon_sign_name=result.chart.moon_sign_name,
        moon_house=result.chart.moon_house,
        moon_nakshatra_number=result.chart.moon_nakshatra_number,
        moon_nakshatra_name=result.chart.moon_nakshatra_name,
        moon_nakshatra_lord_code=result.chart.moon_nakshatra_lord_code,
        seventh_lord_code=result.chart.seventh_lord_code,
        seventh_lord_house=result.chart.seventh_lord_house,
        strongest_planet_code=result.chart.strongest_planet_code,
        strongest_planet_house=result.chart.strongest_planet_house,
        strongest_planet_sign_name=result.chart.strongest_planet_sign_name,
    )

    topic_responses = [
        PrasnaTopicResponse(
            rank=t.rank,
            topic=t.topic,
            confidence=t.confidence,
            primary_house=t.primary_house,
            primary_indicator=t.primary_indicator,
            paragraph=t.paragraph,
        )
        for t in result.topics
    ]

    return PrasnaResponse(
        datetime_utc=result.datetime_utc,
        chart=chart_resp,
        topics=topic_responses,
    )
