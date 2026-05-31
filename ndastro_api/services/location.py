"""Location lookup service backed by an external geocoding provider."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, cast

import httpx
from timezonefinder import TimezoneFinder

from ndastro_api.core.config import settings

_TIMEZONE_FINDER = TimezoneFinder()


class LocationLookupError(RuntimeError):
    """Raised when the configured location provider cannot be reached or parsed."""


@dataclass(frozen=True)
class LocationSearchResult:
    """Normalized location details returned by the provider."""

    name: str
    display_name: str
    lat: float
    lon: float
    timezone: str | None
    country: str | None
    state: str | None
    country_code: str | None
    result_type: str | None
    provider: str = "nominatim"


def search_locations(query: str, limit: int | None = None) -> tuple[LocationSearchResult, ...]:
    """Search locations by free-form text and return normalized matches."""
    normalized_query = query.strip()
    if len(normalized_query) < 2:
        msg = "Query must contain at least 2 characters"
        raise ValueError(msg)

    max_limit = max(1, settings.LOCATION_SERVICE_MAX_LIMIT)
    default_limit = min(max(1, settings.LOCATION_SERVICE_DEFAULT_LIMIT), max_limit)
    resolved_limit = default_limit if limit is None else min(max(1, limit), max_limit)

    return _search_locations_cached(normalized_query, resolved_limit)


@lru_cache(maxsize=256)
def _search_locations_cached(query: str, limit: int) -> tuple[LocationSearchResult, ...]:
    payload = _fetch_candidates(query, limit)
    if not isinstance(payload, list):
        msg = "Location provider returned an unexpected payload"
        raise LocationLookupError(msg)

    results: list[LocationSearchResult] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        result = _build_result(item)
        if result is not None:
            results.append(result)

    return tuple(results)


def _fetch_candidates(query: str, limit: int) -> Any:
    provider_urls = (settings.LOCATION_SERVICE_URL, *settings.LOCATION_SERVICE_FALLBACK_URLS)
    errors: list[str] = []
    for provider_url in provider_urls:
        try:
            return _request_candidates(provider_url, query, limit)
        except LocationLookupError as exc:
            errors.append(f"{provider_url}: {exc}")

    msg = "Location provider request failed"
    if errors:
        msg = f"{msg}: {'; '.join(errors)}"
    raise LocationLookupError(msg)


def _request_candidates(provider_url: str, query: str, limit: int) -> Any:
    headers = {"User-Agent": settings.LOCATION_SERVICE_USER_AGENT}
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": limit,
    }

    try:
        with httpx.Client(timeout=settings.LOCATION_SERVICE_TIMEOUT_SECONDS, headers=headers, follow_redirects=True) as client:
            response = client.get(provider_url, params=params)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = "Location provider request failed"
        raise LocationLookupError(msg) from exc

    try:
        return response.json()
    except ValueError as exc:
        msg = "Location provider returned invalid JSON"
        raise LocationLookupError(msg) from exc


def _build_result(item: dict[str, Any]) -> LocationSearchResult | None:
    try:
        lat = float(item["lat"])
        lon = float(item["lon"])
    except (KeyError, TypeError, ValueError):
        return None

    address_raw = item.get("address")
    address = cast(dict[str, Any], address_raw) if isinstance(address_raw, dict) else {}
    display_name = str(item.get("display_name") or "").strip()
    primary_name = _pick_primary_name(item, address, display_name)
    country_code = _normalize_str(address.get("country_code"))
    timezone_name = _TIMEZONE_FINDER.timezone_at(lat=lat, lng=lon)

    return LocationSearchResult(
        name=primary_name,
        display_name=display_name or primary_name,
        lat=lat,
        lon=lon,
        timezone=timezone_name,
        country=_normalize_str(address.get("country")),
        state=_normalize_str(address.get("state") or address.get("region") or address.get("county")),
        country_code=country_code.upper() if country_code is not None else None,
        result_type=_normalize_str(item.get("type") or item.get("addresstype")),
    )


def _pick_primary_name(item: dict[str, Any], address: dict[str, Any], display_name: str) -> str:
    candidates = (
        item.get("name"),
        address.get("city"),
        address.get("town"),
        address.get("village"),
        address.get("municipality"),
        address.get("county"),
        address.get("state"),
        address.get("country"),
    )
    for candidate in candidates:
        normalized = _normalize_str(candidate)
        if normalized:
            return normalized
    if display_name:
        return display_name.split(",", maxsplit=1)[0].strip()
    return "Unknown location"


def _normalize_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None