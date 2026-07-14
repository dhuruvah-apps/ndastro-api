"""API tests for GET /api/v1/muhurta/auspicious-range."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from ndastro_api.main import app
from ndastro_api.services.muhurta_range import AuspiciousDateResult, EventType, TimeWindowSummary

BASE_PARAMS = {
    "start_date": "2026-08-01",
    "end_date": "2026-08-03",
    "event": "marriage",
    "lat": 12.971667,
    "lon": 77.593611,
    "ayanamsa": "lahiri",
    "limit": 10,
}


def _make_result(score: float = 10.5, d: str = "2026-08-01") -> AuspiciousDateResult:
    return AuspiciousDateResult(
        date=d, event="marriage", score=score,
        tithi_number=2, tithi_name="Dwitiya", paksha="shukla",
        vara_number=5, vara_name="Thursday",
        nakshatra=4, yoga_name="Siddhi", yoga_number=16,
        muhurta_rating=8.0,
        tithi_support=True, karana_support=False, vara_support=True, yoga_support=True,
        inauspicious_flags=[],
        supporting_reasons=["Tithi Dwitiya (2) is auspicious for marriage"],
        caution_reasons=[],
        abhijit_muhurta=TimeWindowSummary(
            name="abhijit_muhurta",
            start="2026-08-01T11:45:00+00:00",
            end="2026-08-01T12:30:00+00:00",
            duration_minutes=45.0,
        ),
        rahu_kalam=TimeWindowSummary(
            name="rahu_kalam",
            start="2026-08-01T07:30:00+00:00",
            end="2026-08-01T09:00:00+00:00",
            duration_minutes=90.0,
        ),
        yamagandam=None,
        gulika=None,
        sunrise="2026-08-01T06:00:00+00:00",
        sunset="2026-08-01T18:30:00+00:00",
    )


class TestAuspiciousRangeEndpoint:
    def test_returns_200_with_valid_params(self) -> None:
        results = (_make_result(10.5, "2026-08-01"), _make_result(8.0, "2026-08-02"))
        with patch("ndastro_api.api.v1.muhurta.search_auspicious_dates", return_value=results):
            response = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=BASE_PARAMS)

        assert response.status_code == 200

    def test_response_shape(self) -> None:
        results = (_make_result(10.5),)
        with patch("ndastro_api.api.v1.muhurta.search_auspicious_dates", return_value=results):
            payload = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=BASE_PARAMS).json()

        assert payload["event"] == "marriage"
        assert payload["start_date"] == "2026-08-01"
        assert payload["end_date"] == "2026-08-03"
        assert payload["total_found"] == 1
        assert len(payload["results"]) == 1

    def test_result_fields_are_present(self) -> None:
        results = (_make_result(10.5),)
        with patch("ndastro_api.api.v1.muhurta.search_auspicious_dates", return_value=results):
            payload = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=BASE_PARAMS).json()

        r = payload["results"][0]
        assert r["date"] == "2026-08-01"
        assert r["score"] == pytest.approx(10.5)
        assert r["tithi_name"] == "Dwitiya"
        assert r["paksha"] == "shukla"
        assert r["vara_name"] == "Thursday"
        assert r["nakshatra"] == 4
        assert r["yoga_name"] == "Siddhi"
        assert r["tithi_support"] is True
        assert r["vara_support"] is True
        assert r["inauspicious_flags"] == []
        assert "Tithi Dwitiya" in r["supporting_reasons"][0]

    def test_abhijit_and_rahu_kalam_nested(self) -> None:
        results = (_make_result(10.5),)
        with patch("ndastro_api.api.v1.muhurta.search_auspicious_dates", return_value=results):
            r = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=BASE_PARAMS).json()["results"][0]

        assert r["abhijit_muhurta"]["name"] == "abhijit_muhurta"
        assert r["abhijit_muhurta"]["duration_minutes"] == pytest.approx(45.0)
        assert r["rahu_kalam"]["name"] == "rahu_kalam"
        assert r["yamagandam"] is None
        assert r["gulika"] is None

    def test_empty_results_returns_200(self) -> None:
        with patch("ndastro_api.api.v1.muhurta.search_auspicious_dates", return_value=()):
            payload = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=BASE_PARAMS).json()

        assert payload["total_found"] == 0
        assert payload["results"] == []

    def test_service_called_with_correct_arguments(self) -> None:
        with patch("ndastro_api.api.v1.muhurta.search_auspicious_dates", return_value=()) as mock_search:
            TestClient(app).get("/api/v1/muhurta/auspicious-range", params=BASE_PARAMS)

        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args.kwargs
        assert call_kwargs["start_date"] == date(2026, 8, 1)
        assert call_kwargs["end_date"] == date(2026, 8, 3)
        assert call_kwargs["event"] == EventType.MARRIAGE
        assert call_kwargs["lat"] == pytest.approx(12.971667)
        assert call_kwargs["lon"] == pytest.approx(77.593611)
        assert call_kwargs["limit"] == 10

    def test_min_score_forwarded_to_service(self) -> None:
        with patch("ndastro_api.api.v1.muhurta.search_auspicious_dates", return_value=()) as mock_search:
            TestClient(app).get("/api/v1/muhurta/auspicious-range", params=BASE_PARAMS | {"min_score": 9.0})

        assert mock_search.call_args.kwargs["min_score"] == pytest.approx(9.0)

    def test_all_event_types_accepted(self) -> None:
        client = TestClient(app)
        with patch("ndastro_api.api.v1.muhurta.search_auspicious_dates", return_value=()):
            for event in EventType:
                params = BASE_PARAMS | {"event": event.value}
                response = client.get("/api/v1/muhurta/auspicious-range", params=params)
                assert response.status_code == 200, f"Unexpected status for event={event.value}"


class TestAuspiciousRangeValidation:
    def test_invalid_date_format_returns_400(self) -> None:
        params = BASE_PARAMS | {"start_date": "01-08-2026"}
        response = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=params)
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]["message"]

    def test_missing_required_params_returns_422(self) -> None:
        response = TestClient(app).get("/api/v1/muhurta/auspicious-range", params={"lat": 12.97})
        assert response.status_code == 422

    def test_invalid_event_type_returns_422(self) -> None:
        params = BASE_PARAMS | {"event": "moonwalk"}
        response = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=params)
        assert response.status_code == 422

    def test_date_range_too_large_returns_400(self) -> None:
        with patch(
            "ndastro_api.api.v1.muhurta.search_auspicious_dates",
            side_effect=ValueError("Date range must not exceed 365 days"),
        ):
            params = BASE_PARAMS | {"start_date": "2025-01-01", "end_date": "2026-12-31"}
            response = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=params)

        assert response.status_code == 400
        assert "365 days" in response.json()["detail"]["message"]

    def test_end_before_start_returns_400(self) -> None:
        with patch(
            "ndastro_api.api.v1.muhurta.search_auspicious_dates",
            side_effect=ValueError("end_date must be on or after start_date"),
        ):
            params = BASE_PARAMS | {"start_date": "2026-09-01", "end_date": "2026-08-01"}
            response = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=params)

        assert response.status_code == 400

    def test_limit_below_minimum_returns_422(self) -> None:
        params = BASE_PARAMS | {"limit": 0}
        response = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=params)
        assert response.status_code == 422

    def test_limit_above_maximum_returns_422(self) -> None:
        params = BASE_PARAMS | {"limit": 101}
        response = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=params)
        assert response.status_code == 422

    def test_min_score_below_zero_returns_422(self) -> None:
        params = BASE_PARAMS | {"min_score": -1.0}
        response = TestClient(app).get("/api/v1/muhurta/auspicious-range", params=params)
        assert response.status_code == 422
