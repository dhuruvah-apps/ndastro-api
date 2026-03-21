"""Services for calculating kattams (astrological charts) based on given datetime and location.

This module provides functions to compute kattams using planetary positions, ascendant, and ayanamsa.
"""

from datetime import datetime
from itertools import groupby
from typing import cast

from ndastro_engine.house_enum import Houses
from ndastro_engine.planet_enum import Planets
from ndastro_engine.rasi_enum import RasiCode, Rasis

from ndastro_api.core.constants import TOTAL_RAASI
from ndastro_api.core.models.kattam import Kattam
from ndastro_api.services.position import get_sidereal_planet_positions


def get_kattams(lat: float, lon: float, given_time: datetime, ayanamsa: float) -> list[Kattam]:
    """Return the kattams for the given datetime, latitude, and longitude.

    Args:
        lat (float): The latitude of the observer.
        lon (float): The longitude of the observer.
        given_time (datetime): The datetime of the observation.
        ayanamsa (float): The ayanamsa value to use for calculations.

    Returns:
        list[Kattam]: A list of kattams.

    """
    planets = get_sidereal_planet_positions(lat, lon, given_time, ayanamsa)

    ascendant = next((p for p in planets if p.code == Planets.ASCENDANT.code), None)

    if ascendant is None:
        msg = "Ascendant can't be None"
        raise ValueError(msg)

    rasis_planets = {
        k: list(g) for k, g in groupby(sorted(planets, key=lambda x: 0 if x.rasi_occupied is None else x.rasi_occupied), lambda x: x.rasi_occupied)
    }

    kattams: list[Kattam] = []
    rasi_list = list(range(1, TOTAL_RAASI + 1))
    normalized_rasi_list = (
        rasi_list[cast("Rasis", Rasis.from_code(cast("RasiCode", ascendant.rasi_occupied))).value - 1 :]
        + rasi_list[: cast("Rasis", Rasis.from_code(cast("RasiCode", ascendant.rasi_occupied))).value - 1]
    )
    for idx, rasi_num in enumerate(normalized_rasi_list):
        rasi = Rasis(rasi_num)
        rp = rasis_planets.get(rasi.code, [])
        kattam = Kattam(
            order=rasi_num,
            owner=cast("Planets", rasi.owner),
            is_ascendant=ascendant.rasi_occupied == rasi.code,
            planets=rp,
            rasi=rasi,
            house=Houses(idx + 1),
            asc_longitude=ascendant.longitude if ascendant.rasi_occupied == rasi.code else None,
        )
        kattams.append(kattam)

    kattams.sort(key=lambda x: x.order)

    return kattams
