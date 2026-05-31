from __future__ import annotations

from unittest.mock import patch

from starlette.testclient import TestClient

from ndastro_api.main import app
from ndastro_api.services.location import LocationLookupError, LocationSearchResult


def test_location_search_returns_normalized_results() -> None:
    client = TestClient(app)
    mocked_results = (
        LocationSearchResult(
            name="Salem",
            display_name="Salem, Tamil Nadu, India",
            lat=11.664325,
            lon=78.146011,
            timezone="Asia/Kolkata",
            country="India",
            state="Tamil Nadu",
            country_code="IN",
            result_type="city",
        ),
    )

    with patch("ndastro_api.api.v1.location.search_locations", return_value=mocked_results):
        response = client.get("/api/v1/location/search", params={"q": "Salem", "limit": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "Salem"
    assert payload["count"] == 1
    assert payload["results"][0]["lat"] == 11.664325
    assert payload["results"][0]["lon"] == 78.146011
    assert payload["results"][0]["timezone"] == "Asia/Kolkata"


def test_location_search_returns_502_for_provider_failure() -> None:
    client = TestClient(app)

    with patch("ndastro_api.api.v1.location.search_locations", side_effect=LocationLookupError("Location provider request failed")):
        response = client.get("/api/v1/location/search", params={"q": "Salem"})

    assert response.status_code == 502
    assert response.json()["detail"]["message"] == "Location provider request failed"


def test_location_search_validates_query_length() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/location/search", params={"q": "a"})

    assert response.status_code == 422