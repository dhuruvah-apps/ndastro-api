from __future__ import annotations

from unittest.mock import Mock, patch

import httpx
import pytest

from ndastro_api.services.location import LocationLookupError, _search_locations_cached, search_locations


@pytest.fixture(autouse=True)
def clear_location_cache() -> None:
    _search_locations_cached.cache_clear()
    yield
    _search_locations_cached.cache_clear()


def test_search_locations_maps_provider_payload() -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = [
        {
            "name": "Salem",
            "display_name": "Salem, Tamil Nadu, India",
            "lat": "11.6643",
            "lon": "78.1460",
            "type": "city",
            "address": {
                "city": "Salem",
                "state": "Tamil Nadu",
                "country": "India",
                "country_code": "in",
            },
        }
    ]
    client = Mock()
    client.get.return_value = response
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=None)

    with patch("ndastro_api.services.location.httpx.Client", return_value=client):
        results = search_locations("Salem", 3)

    assert len(results) == 1
    assert results[0].name == "Salem"
    assert results[0].lat == pytest.approx(11.6643)
    assert results[0].lon == pytest.approx(78.1460)
    assert results[0].country == "India"
    assert results[0].country_code == "IN"
    assert results[0].timezone == "Asia/Kolkata"


def test_search_locations_rejects_short_queries() -> None:
    with pytest.raises(ValueError, match="at least 2 characters"):
        search_locations("a")


def test_search_locations_wraps_provider_failures() -> None:
    client = Mock()
    client.get.side_effect = httpx.ReadTimeout("boom")
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=None)

    with patch("ndastro_api.services.location.httpx.Client", return_value=client):
        with pytest.raises(LocationLookupError, match="request failed"):
            search_locations("Salem")


def test_search_locations_uses_cache_for_repeat_queries() -> None:
    payload = [
        {
            "name": "Salem",
            "display_name": "Salem, Tamil Nadu, India",
            "lat": "11.6643",
            "lon": "78.1460",
            "address": {"country": "India", "country_code": "in"},
        }
    ]

    with patch("ndastro_api.services.location._fetch_candidates", return_value=payload) as fetch_candidates:
        first = search_locations("Salem", 2)
        second = search_locations("Salem", 2)

    assert first == second
    assert fetch_candidates.call_count == 1


def test_search_locations_falls_back_to_secondary_provider() -> None:
    primary_url = "https://primary.example/search"
    fallback_url = "https://fallback.example/search"

    def fake_request(provider_url: str, query: str, limit: int):
        if provider_url == primary_url:
            raise LocationLookupError("primary down")
        assert provider_url == fallback_url
        assert query == "Salem"
        assert limit == 2
        return [
            {
                "name": "Salem",
                "display_name": "Salem, Tamil Nadu, India",
                "lat": "11.6643",
                "lon": "78.1460",
                "address": {"country": "India", "country_code": "in"},
            }
        ]

    with patch("ndastro_api.services.location.settings.LOCATION_SERVICE_URL", primary_url), patch(
        "ndastro_api.services.location.settings.LOCATION_SERVICE_FALLBACK_URLS",
        [fallback_url],
    ), patch("ndastro_api.services.location._request_candidates", side_effect=fake_request) as request_candidates:
        results = search_locations("Salem", 2)

    assert len(results) == 1
    assert results[0].name == "Salem"
    assert request_candidates.call_count == 2