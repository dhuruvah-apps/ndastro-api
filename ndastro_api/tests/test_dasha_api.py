"""API tests for the rewritten dasha endpoints."""

from __future__ import annotations

from starlette.testclient import TestClient

from ndastro_api.main import app

BASE_QUERY = {
    "lat": 12.971667,
    "lon": 77.593611,
    "ayanamsa": "lahiri",
    "dateandtime": "2026-04-18T00:00:00+05:30",
}


def test_dasha_types_lists_vimshottari() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/dasha/types")

    assert response.status_code == 200
    assert "vimshottari" in response.json()["supported_types"]


def test_current_dasha_returns_detailed_running_periods() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/dasha/vimshottari/current", params=BASE_QUERY)

    assert response.status_code == 200
    payload = response.json()
    assert payload["dasa_type"] == "vimshottari"
    assert payload["birth_info"]["janma_nakshatra_code"] == "N01"
    assert payload["maha"]["level_name"] == "maha"
    assert payload["maha"]["lord_code"] == "KE"
    assert payload["antara"]["level_name"] == "antara"
    assert payload["sookshma"]["level_name"] == "sookshma"


def test_timeline_supports_nested_levels() -> None:
    client = TestClient(app)
    response = client.get(
        "/api/v1/dasha/vimshottari/timeline",
        params=BASE_QUERY | {"levels": 2, "years": 10},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dasa_type"] == "vimshottari"
    assert payload["query"] == {"levels": 2, "years": 10.0}
    assert len(payload["periods"]) >= 1
    assert payload["periods"][0]["level_name"] == "maha"
    assert payload["periods"][0]["child_count"] > 0
    assert payload["periods"][0]["children"][0]["level_name"] == "antara"


def test_unknown_dasa_type_returns_400() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/dasha/unknown/current", params=BASE_QUERY)

    assert response.status_code == 400
    payload = response.json()["detail"]
    assert "Unsupported dasa type" in payload["message"]
    assert "vimshottari" in payload["supported_types"]