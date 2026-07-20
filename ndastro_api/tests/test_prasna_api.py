"""Unit and API tests for the Prasna (Vedic horary astrology) service and endpoint.

Low-level helpers are tested directly.
The main service function is tested via mocks so no live ephemeris is needed.
The API endpoint is tested with a mock of analyse_prasna_query.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from ndastro_api.core.models.prasna import PrasnaChartSnapshot, PrasnaResult, PrasnaTopicResult
from ndastro_api.main import app
from ndastro_api.services.prasna import (
    _house,
    _ord,
    _planet_strength,
    _primary_indicator,
    _sign,
    analyse_prasna_query,
)


# ---------------------------------------------------------------------------
# _sign — sidereal longitude → 0-indexed sign
# ---------------------------------------------------------------------------

class TestSign:
    def test_aries_start(self) -> None:
        assert _sign(0.0) == 0

    def test_aries_end(self) -> None:
        assert _sign(29.99) == 0

    def test_taurus(self) -> None:
        assert _sign(30.0) == 1

    def test_pisces(self) -> None:
        assert _sign(359.0) == 11

    def test_wraps_at_360(self) -> None:
        assert _sign(360.0) == 0

    def test_virgo(self) -> None:
        assert _sign(150.0) == 5     # 150 / 30 = 5 → Virgo


# ---------------------------------------------------------------------------
# _house — whole-sign house relative to Lagna
# ---------------------------------------------------------------------------

class TestHouse:
    def test_planet_in_lagna_sign_is_house_1(self) -> None:
        # Lagna = Aries (0), planet in Aries
        assert _house(15.0, 0) == 1

    def test_planet_one_sign_ahead_is_house_2(self) -> None:
        # Lagna = Aries (0), planet in Taurus (lon=45)
        assert _house(45.0, 0) == 2

    def test_7th_house_from_aries_is_libra(self) -> None:
        # Lagna = Aries (0), planet at Libra (180°)
        assert _house(180.0, 0) == 7

    def test_wrap_around(self) -> None:
        # Lagna = Libra (6), planet at Aries (0°) → house 7
        assert _house(0.0, 6) == 7

    def test_12th_house(self) -> None:
        # Lagna = Taurus (1), planet at Aries (0-29°) → house 12
        assert _house(15.0, 1) == 12


# ---------------------------------------------------------------------------
# _planet_strength — dignity scoring
# ---------------------------------------------------------------------------

class TestPlanetStrength:
    def test_exaltation_returns_maximum(self) -> None:
        # Sun exalted in Aries (sign 0)
        assert _planet_strength("SU", 0) == pytest.approx(3.0)

    def test_debilitation_returns_minimum(self) -> None:
        # Sun debilitated in Libra (sign 6)
        assert _planet_strength("SU", 6) == pytest.approx(0.25)

    def test_own_sign_returns_high(self) -> None:
        # Moon owns Cancer (sign 3)
        assert _planet_strength("MO", 3) == pytest.approx(2.5)

    def test_friendly_sign_returns_good(self) -> None:
        # Sun in Aries is own; in Sagittarius (8, ruled by JU who is Sun's friend)
        assert _planet_strength("SU", 8) == pytest.approx(2.0)

    def test_enemy_sign_returns_low(self) -> None:
        # Sun enemy of Saturn; Capricorn (9) ruled by Saturn
        assert _planet_strength("SU", 9) == pytest.approx(0.8)

    def test_neutral_sign_returns_mid(self) -> None:
        # Mercury in Scorpio (7, ruled by Mars — neutral for Mercury)
        # Mars is not in Mercury's friend or enemy list
        assert _planet_strength("ME", 7) == pytest.approx(1.5)


# ---------------------------------------------------------------------------
# _ord — ordinal formatting
# ---------------------------------------------------------------------------

class TestOrd:
    @pytest.mark.parametrize("n,expected", [
        (1, "1st"), (2, "2nd"), (3, "3rd"), (4, "4th"),
        (7, "7th"), (10, "10th"), (11, "11th"), (12, "12th"),
    ])
    def test_ordinals(self, n: int, expected: str) -> None:
        assert _ord(n) == expected


# ---------------------------------------------------------------------------
# _primary_indicator — selector logic
# ---------------------------------------------------------------------------

class TestPrimaryIndicator:
    def test_moon_house_wins(self) -> None:
        result = _primary_indicator(
            house=7, moon_house=7,
            lagna_lord="MA", lagna_lord_house=3,
            seventh_lord="VE", seventh_lord_house=2,
            strongest_planet="JU", strongest_planet_house=10,
            moon_nak_lord="MO",
        )
        assert "Moon" in result and "7th" in result

    def test_seventh_lord_used_when_house_matches(self) -> None:
        result = _primary_indicator(
            house=4, moon_house=7,      # Moon not in house 4
            lagna_lord="MA", lagna_lord_house=3,
            seventh_lord="VE", seventh_lord_house=4,
            strongest_planet="JU", strongest_planet_house=10,
            moon_nak_lord="MO",
        )
        assert "Venus" in result or "7th" in result

    def test_lagna_lord_used_when_house_matches(self) -> None:
        result = _primary_indicator(
            house=5, moon_house=7,
            lagna_lord="MA", lagna_lord_house=5,
            seventh_lord="VE", seventh_lord_house=2,
            strongest_planet="JU", strongest_planet_house=10,
            moon_nak_lord="MO",
        )
        assert "Mars" in result or "Lagna" in result

    def test_strongest_planet_fallback(self) -> None:
        result = _primary_indicator(
            house=10, moon_house=7,
            lagna_lord="MA", lagna_lord_house=3,
            seventh_lord="VE", seventh_lord_house=2,
            strongest_planet="JU", strongest_planet_house=10,
            moon_nak_lord="MO",
        )
        assert "Jupiter" in result


# ---------------------------------------------------------------------------
# analyse_prasna_query — integration smoke test (live ephemeris)
# ---------------------------------------------------------------------------

class TestAnalysePrasnaQuery:
    def test_returns_prasna_result_with_three_topics(self) -> None:
        dt = datetime(2026, 4, 18, 0, 0, 0, tzinfo=UTC)
        result = analyse_prasna_query(12.971667, 77.593611, dt)

        assert isinstance(result, PrasnaResult)
        assert len(result.topics) == 3

    def test_topic_ranks_are_1_2_3(self) -> None:
        dt = datetime(2026, 4, 18, 0, 0, 0, tzinfo=UTC)
        result = analyse_prasna_query(12.971667, 77.593611, dt)
        assert [t.rank for t in result.topics] == [1, 2, 3]

    def test_confidence_descending(self) -> None:
        dt = datetime(2026, 4, 18, 0, 0, 0, tzinfo=UTC)
        result = analyse_prasna_query(12.971667, 77.593611, dt)
        confidences = [t.confidence for t in result.topics]
        assert confidences == sorted(confidences, reverse=True)

    def test_confidence_within_range(self) -> None:
        dt = datetime(2026, 4, 18, 0, 0, 0, tzinfo=UTC)
        result = analyse_prasna_query(12.971667, 77.593611, dt)
        for t in result.topics:
            assert 0.0 <= t.confidence <= 1.0

    def test_chart_fields_are_valid(self) -> None:
        dt = datetime(2026, 4, 18, 0, 0, 0, tzinfo=UTC)
        result = analyse_prasna_query(12.971667, 77.593611, dt)
        chart = result.chart
        assert 1 <= chart.lagna_sign_number <= 12
        assert 1 <= chart.moon_sign_number <= 12
        assert 1 <= chart.moon_house <= 12
        assert 1 <= chart.moon_nakshatra_number <= 27
        assert 1 <= chart.lagna_lord_house <= 12
        assert 1 <= chart.seventh_lord_house <= 12
        assert 1 <= chart.strongest_planet_house <= 12

    def test_paragraph_is_non_empty_for_all_topics(self) -> None:
        dt = datetime(2026, 4, 18, 0, 0, 0, tzinfo=UTC)
        result = analyse_prasna_query(12.971667, 77.593611, dt)
        for t in result.topics:
            assert len(t.paragraph) > 50

    def test_naive_datetime_is_handled(self) -> None:
        """Service should not raise when a naive datetime is passed."""
        from datetime import datetime as dt_type
        naive = dt_type(2026, 4, 18, 6, 0, 0)
        result = analyse_prasna_query(12.971667, 77.593611, naive)
        assert len(result.topics) == 3


# ---------------------------------------------------------------------------
# API endpoint — GET /api/v1/prasna/query-topic
# ---------------------------------------------------------------------------

_MOCK_CHART = PrasnaChartSnapshot(
    lagna_sign_number=5, lagna_sign_name="Leo", lagna_lord_code="SU", lagna_lord_house=1,
    moon_sign_number=11, moon_sign_name="Aquarius", moon_house=7,
    moon_nakshatra_number=24, moon_nakshatra_name="Shathayam", moon_nakshatra_lord_code="RA",
    seventh_lord_code="SA", seventh_lord_house=7,
    strongest_planet_code="JU", strongest_planet_house=5, strongest_planet_sign_name="Sagittarius",
)

_MOCK_TOPIC = PrasnaTopicResult(
    rank=1, topic="Marriage & Partnership", confidence=0.82,
    primary_house=7, primary_indicator="Moon occupies the 7th house",
    paragraph=(
        "At the moment of this query, Leo rises as the Lagna with Sun as its lord. "
        "The Moon in Aquarius in the 7th house strongly indicates a relationship question. "
        "Saturn, lord of the 7th, also sits in the 7th — a rare double emphasis. "
        "The indicators point with strong conviction toward a marriage or partnership matter."
    ),
)

_MOCK_RESULT = PrasnaResult(
    datetime_utc="2026-04-18T00:00:00+00:00",
    chart=_MOCK_CHART,
    topics=(_MOCK_TOPIC,),
)


class TestPrasnaEndpoint:
    BASE = {"lat": 12.971667, "lon": 77.593611}

    def test_returns_200(self) -> None:
        with patch("ndastro_api.api.v1.prasna.analyse_prasna_query", return_value=_MOCK_RESULT):
            resp = TestClient(app).get("/api/v1/prasna/query-topic", params=self.BASE)
        assert resp.status_code == 200

    def test_response_shape(self) -> None:
        with patch("ndastro_api.api.v1.prasna.analyse_prasna_query", return_value=_MOCK_RESULT):
            payload = TestClient(app).get("/api/v1/prasna/query-topic", params=self.BASE).json()

        assert "datetime_utc" in payload
        assert "chart" in payload
        assert "topics" in payload
        assert "disclaimer" in payload

    def test_chart_fields_present(self) -> None:
        with patch("ndastro_api.api.v1.prasna.analyse_prasna_query", return_value=_MOCK_RESULT):
            chart = TestClient(app).get("/api/v1/prasna/query-topic", params=self.BASE).json()["chart"]

        assert chart["lagna_sign_name"] == "Leo"
        assert chart["moon_house"] == 7
        assert chart["moon_nakshatra_name"] == "Shathayam"
        assert chart["strongest_planet_code"] == "JU"

    def test_first_topic_fields(self) -> None:
        with patch("ndastro_api.api.v1.prasna.analyse_prasna_query", return_value=_MOCK_RESULT):
            topic = TestClient(app).get("/api/v1/prasna/query-topic", params=self.BASE).json()["topics"][0]

        assert topic["rank"] == 1
        assert topic["topic"] == "Marriage & Partnership"
        assert topic["confidence"] == pytest.approx(0.82)
        assert "Moon" in topic["primary_indicator"]
        assert len(topic["paragraph"]) > 20

    def test_missing_lat_lon_returns_422(self) -> None:
        resp = TestClient(app).get("/api/v1/prasna/query-topic", params={"lat": 12.97})
        assert resp.status_code == 422

    def test_custom_datetime_forwarded(self) -> None:
        params = self.BASE | {"dateandtime": "2026-01-01T06:00:00+05:30"}
        with patch("ndastro_api.api.v1.prasna.analyse_prasna_query", return_value=_MOCK_RESULT) as mock:
            TestClient(app).get("/api/v1/prasna/query-topic", params=params)
        called_dt = mock.call_args[0][2]  # 3rd positional arg = dt
        assert called_dt.year == 2026 and called_dt.month == 1

    def test_disclaimer_is_present(self) -> None:
        with patch("ndastro_api.api.v1.prasna.analyse_prasna_query", return_value=_MOCK_RESULT):
            payload = TestClient(app).get("/api/v1/prasna/query-topic", params=self.BASE).json()
        assert "Prasna Shastra" in payload["disclaimer"]
