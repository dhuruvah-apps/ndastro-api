"""Utility functions for astronomical calculations and planetary positions.

This module provides helper functions for degree normalization, DMS conversion,
and filtering planetary positions by rasi, using constants and models from ndastro_api.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from ndastro_api.core.constants import DEGREE_MAX, TOTAL_RAASI

if TYPE_CHECKING:
    from ndastro_api.core.models.kattam import Kattam


def sign(num: int) -> int:
    """Return the sign of the given number.

    Args:
        num (int): The number to get the sign from.

    Returns:
        int: -1 if the number is negative, otherwise 1.

    """
    return -1 if num < 0 else 1


def dms_to_decimal(degrees: int, minutes: int, seconds: float) -> float:
    """Convert degrees, minutes, and seconds to decimal degrees.

    Args:
        degrees (int): The degrees part.
        minutes (int): The minutes part.
        seconds (float): The seconds part.

    Returns:
        float: The decimal degrees.

    """
    return degrees + minutes / 60 + seconds / 3600


def normalize_degree(degree: float) -> float:
    """Normalize the degree to be within 0-360.

    Args:
        degree (float): The degree to normalize.

    Returns:
        float: The normalized degree.

    """
    if degree < 0:
        return DEGREE_MAX + degree
    while degree > DEGREE_MAX:
        degree -= DEGREE_MAX
    return degree


def normalize_rasi_house(position: int) -> int:
    """Normalize the rasi position to be within 1-12.

    Args:
        position (int): The rasi position to normalize.

    Returns:
        int: The normalized rasi position.

    """
    if position < 0:
        return TOTAL_RAASI + position
    while position > TOTAL_RAASI:
        position -= TOTAL_RAASI
    return position


def compute_offset(page: int, items_per_page: int) -> int:
    """Compute the offset for pagination based on page and items per page."""
    return max((page - 1) * items_per_page, 0)


def paginated_response(*, crud_data: Any, page: int, items_per_page: int) -> dict[str, Any]:  # noqa: ANN401
    """Build a paginated response dictionary for list endpoints.

    Args:
        crud_data: An object or list containing the data to paginate. If an object, it should have 'items' and optionally 'total' attributes.
        page (int): The current page number (1-based).
        items_per_page (int): The number of items per page.

    Returns:
        dict: A dictionary containing:
            - items: The list of items for the current page.
            - total: The total number of items.
            - page: The current page number.
            - items_per_page: The number of items per page.
            - next_page: The next page number, or None if there is no next page.
            - prev_page: The previous page number, or None if there is no previous page.

    """
    """Build a paginated response dict for list endpoints."""
    items = crud_data.get("data", [])
    total_count = crud_data.get("total_count", 0)

    return {
        "items": items,
        "total": total_count,
        "total_count": total_count,
        "has_more": (page * items_per_page) < total_count,
        "page": page,
        "items_per_page": items_per_page,
    }


def convert_kattams_to_response_format(kattams: list[Kattam], kattam_response_class: type, planet_detail_response_class: type) -> list:
    """Convert kattams service response to KattamResponse format.

    This utility function handles the conversion of raw kattam data from the service
    to the standardized KattamResponse format used by API endpoints.

    Args:
        kattams: List of raw kattam objects from the service
        kattam_response_class: The KattamResponse class to use for conversion
        planet_detail_response_class: The PlanetDetailResponse class to use for conversion

    Returns:
        List of objects in KattamResponse format

    """
    return [
        kattam_response_class(
            order=k.order,
            is_ascendant=k.is_ascendant,
            asc_longitude=cast("float", k.asc_longitude) if k.asc_longitude is not None else 0.0,
            owner=k.owner,
            rasi=k.rasi.value,
            house=k.house.value,
            planets=k.planets,
        )
        for k in kattams
    ]
