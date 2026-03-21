"""Services for astronomical position calculations.

This module provides functions to compute tropical and sidereal planetary positions,
ascendant, lunar nodes, nakshatra and pada, as well as sunrise and sunset times
using the Skyfield library and domain-specific models.
"""

from __future__ import annotations

from dataclasses import asdict
from math import ceil, floor
from typing import TYPE_CHECKING, cast

from ndastro_engine.core import get_ascendent_position, get_planets_position
from ndastro_engine.enums import Houses, NakshatraCode, Planets, Rasis
from ndastro_engine.retrograde import is_planet_in_retrograde
from skyfield.units import Angle

from ndastro_api.core.constants import (
    AYANAMSA,
    DEGREE_MAX,
    DEGREES_PER_RAASI,
    TOTAL_NAKSHATRAS,
)
from ndastro_api.core.models.astro_system import Planet
from ndastro_api.core.utils.data_loader import astro_data
from ndastro_api.services.utils import normalize_degree, normalize_rasi_house

if TYPE_CHECKING:
    from datetime import datetime


def get_sidereal_planet_positions(lat: float, lon: float, given_time: datetime, ayanamsa: float) -> list[Planet]:
    """Return the sidereal positions of the planets.

    Args:
        lat (float): The latitude of the observer.
        lon (float): The longitude of the observer.
        given_time (datetime): The datetime of the observation.
        ayanamsa (float): The ayanamsa value to be used for calculation.

    Returns:
        list[Planet]: A list of sidereal positions of the planets.

    """
    planets_positions = get_planets_position([], lat, lon, given_time)
    ascendant = planets_positions.get(Planets.ASCENDANT, None)

    positions: list[Planet] = []

    # Convert dict items to list to avoid "dictionary changed size during iteration" error
    for planet_enum, pos_detail in list(planets_positions.items()):
        if planet_enum == Planets.EMPTY:
            continue

        planet = astro_data.get_planet_by_astronomical_code(planet_enum.astronomical_code)

        # Use the actual longitude from position data
        asc = normalize_degree(pos_detail.longitude - ayanamsa)
        asc_h, asc_adv_by = divmod(asc, DEGREES_PER_RAASI)
        rasi_num = int(asc_h)

        # Calculate position-specific values
        nakshatra, pada = get_nakshatra_and_pada(asc)
        rasi_occupied = Rasis(normalize_rasi_house(rasi_num if asc_adv_by == 0 else int(rasi_num + 1))).code

        posited_at = Houses.HOUSE1.code if ascendant is None else get_planet_house_position(ascendant.longitude, pos_detail.longitude).code

        # Calculate retrograde status
        retrograde = (
            True
            if planet and planet.code in [Planets.RAHU.code, Planets.KETHU.code]
            else is_planet_in_retrograde(given_time, planet.astronomical_code, lat, lon)[0]
            if planet
            else False
        )

        # Build Planet instance with calculated fields
        if planet:
            planet_dict = asdict(planet)
            # Copy essential fields from the base planet data
            planet_data = {
                "latitude": pos_detail.latitude if hasattr(pos_detail, "latitude") else 0.0,
                "longitude": asc,
                "nirayana_longitude": asc,
                "posited_at": posited_at,
                "advanced_by": asc_adv_by,
                "is_retrograde": retrograde,
                "is_ascendant": planet.astronomical_code == Planets.ASCENDANT.astronomical_code,
                "nakshatra": nakshatra,
                "pada": pada,
                "rasi_occupied": rasi_occupied,
            }

            merged_dict = planet_dict | planet_data
            planet_instance = Planet(**merged_dict)

        else:
            # Use minimal defaults when planet lookup fails
            planet_data = {
                "latitude": pos_detail.latitude if hasattr(pos_detail, "latitude") else 0.0,
                "longitude": asc,
                "nirayana_longitude": asc,
                "posited_at": posited_at,
                "advanced_by": asc_adv_by,
                "is_retrograde": retrograde,
                "is_ascendant": False,
                "nakshatra": nakshatra,
                "pada": pada,
                "rasi_occupied": rasi_occupied,
            }
            planet_instance = Planet(**planet_data)

        positions.append(planet_instance)

    return positions


def get_sidereal_ascendant_position(given_time: datetime, lat: float, lon: float, ayanamsa: float = AYANAMSA.LAHIRI) -> Planet:
    """Calculate the sidereal ascendant.

    Args:
        given_time (datetime): The datetime of the observation.
        lat (float): The latitude of the observer.
        lon (float): The longitude of the observer.
        ayanamsa (float): The ayanamsa value to be used for calculation.

    Returns:
        Planet: The position of the sidereal ascendant.

    """
    ascr = get_ascendent_position(lat, lon, given_time)

    # Try to get ASCENDANT planet details from data source
    ascendant_planet = astro_data.get_planet_by_astronomical_code(Planets.ASCENDANT.astronomical_code)

    asc = normalize_degree(ascr - ayanamsa)

    asc_h, asc_adv_by = divmod(asc, DEGREES_PER_RAASI)
    rasi_num = int(asc_h)
    rasi_occupied = Rasis(normalize_rasi_house(rasi_num if asc_adv_by == 0 else int(rasi_num + 1))).code
    posited_at = Houses.HOUSE1.code

    nakshatra, pada = get_nakshatra_and_pada(asc)

    # Build Planet with all ascendant details
    if ascendant_planet:
        planet_dict = asdict(ascendant_planet)
        planet_data = {
            "latitude": 0,
            "longitude": asc,
            "nirayana_longitude": asc,
            "posited_at": posited_at,
            "advanced_by": asc_adv_by,
            "is_ascendant": True,
            "nakshatra": nakshatra,
            "pada": pada,
            "rasi_occupied": rasi_occupied,
            "planet": Planets.ASCENDANT.code,
            "is_retrograde": False,
        }
        merged_dict = planet_dict | planet_data
        planet_instance = Planet(**merged_dict)
    else:
        # Use minimal defaults when planet lookup fails
        planet_data = {
            "latitude": 0,
            "longitude": asc,
            "nirayana_longitude": asc,
            "posited_at": posited_at,
            "advanced_by": asc_adv_by,
            "is_ascendant": True,
            "nakshatra": nakshatra,
            "pada": pada,
            "rasi_occupied": rasi_occupied,
            "planet": Planets.ASCENDANT.code,
            "is_retrograde": False,
        }
        planet_instance = Planet(**planet_data)

    return planet_instance


def get_nakshatra_and_pada(longitude: float) -> tuple[NakshatraCode, int]:
    """Get the nakshatra and pada from the planet longitude.

    Args:
        longitude (float): The longitude of the planet.

    Returns:
        tuple[NakshatraCode, int]: The nakshatra and pada.

    """
    degrees_per_nakshatra = Angle(degrees=DEGREE_MAX / TOTAL_NAKSHATRAS)

    total_degrees_mins = cast("float", Angle(degrees=longitude).arcminutes())

    nakshatra_index = total_degrees_mins / degrees_per_nakshatra.arcminutes()

    remainder = nakshatra_index - floor(nakshatra_index)
    pada_threshold_1 = 0.25
    pada_threshold_2 = 0.5
    pada_threshold_3 = 0.75

    if remainder < pada_threshold_1:
        pada = 1
    elif remainder < pada_threshold_2:
        pada = 2
    elif remainder < pada_threshold_3:
        pada = 3
    else:
        pada = 4

    nakshatra_num = ceil(nakshatra_index + 1 if nakshatra_index == 0 else nakshatra_index)

    # Get nakshatra code from data loader using number
    nakshatra_data = astro_data.get_nakshatra_by_number(nakshatra_num)
    nakshatra_code = cast("NakshatraCode", nakshatra_data.code if nakshatra_data else "")

    return nakshatra_code, pada


def get_planet_sign_and_degree(planet_longitude: float) -> tuple[Rasis, Angle]:
    """Calculate the zodiac sign and degree of a planet based on its longitude.

    Args:
        planet_longitude (float): The longitude of the planet.

    Returns:
        tuple[Rasis, Angle]: A tuple containing the zodiac sign (Rasis) and the
        degree (Angle) of the planet within that sign.

    """
    longitude = cast("float", planet_longitude % DEGREE_MAX)
    sign_index = int(longitude // DEGREES_PER_RAASI)
    degree_within_sign = longitude % DEGREES_PER_RAASI

    return Rasis(normalize_rasi_house(sign_index)), Angle(degrees=degree_within_sign)


def get_planet_house_position(ascendant_longitude: float, planet_longitude: float) -> Houses:
    """Calculate the house position of a planet based on the ascendant and planet longitudes.

    Args:
        ascendant_longitude (float): The longitude of the ascendant.
        planet_longitude (float): The longitude of the planet.

    Returns:
        Houses: The house position of the planet.

    """
    relative_longitude = normalize_degree(planet_longitude - ascendant_longitude)
    house_index = int(relative_longitude // DEGREES_PER_RAASI)

    # Convert 0-based index to 1-based house number (1-12)
    house_number = normalize_rasi_house(house_index + 1)

    return Houses(house_number)
