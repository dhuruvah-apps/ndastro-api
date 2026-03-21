"""Advanced Muhurta timing - Durmuhurta, Varjyam, Amrita/Kala, Tarabala.

Provides specialized muhurta calculations for precise electional astrology.
"""

from __future__ import annotations

import datetime as datetime_module
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


MINUTES_PER_DAY = 1440
MUUURTAS_PER_DAY = 30
MINUTES_PER_MUHURTA = MINUTES_PER_DAY / MUUURTAS_PER_DAY
NAKSHATRAS = 27

# Durmuhurta timings (in muhurta index, 1-30)
DURMUHURTA_INDICES = [6, 14, 23, 28]

# Varjyam nakshatra pairs (inauspicious combinations)
VARJYAM_NAKSHATRA_PAIRS = [
    (1, 3),  # Ashwini, Krittika
    (2, 6),  # Bharani, Ardra
    (4, 8),  # Rohini, Pushya
    (5, 13),  # Mrigashira, Hasta
    (7, 15),  # Punarvasu, Swati
    (9, 17),  # Ashlesha, Anuradha
    (10, 22),  # Magha, Shravana
    (11, 19),  # Purva Phalguni, Mula
    (12, 16),  # Uttara Phalguni, Vishakha
    (14, 24),  # Chitra, Shatabhisha
    (18, 26),  # Jyeshtha, Uttara Bhadrapada
    (20, 27),  # Purva Ashadha, Revati
]


class MuhurtaQuality(str, Enum):
    """Quality classification for muhurtas."""

    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    INAUSPICIOUS = "inauspicious"


@dataclass
class TimeWindow:
    """Represents a time window."""

    start: datetime
    end: datetime
    duration_minutes: float


@dataclass
class DurmuhurtaWindow:
    """Durmuhurta (inauspicious muhurta) timing."""

    window: TimeWindow
    muhurta_index: int
    description: str


@dataclass
class VarjyamWindow:
    """Varjyam (void) timing."""

    window: TimeWindow
    tithi: int
    nakshatra: int
    description: str


@dataclass
class AmritaKalaWindow:
    """Amrita (nectar time) or Kala (death time) window."""

    window: TimeWindow
    quality: str  # "amrita" or "kala"
    weekday: int
    nakshatra: int
    description: str


@dataclass
class AdvancedMuhurtaReport:
    """Complete advanced muhurta analysis."""

    date: datetime
    durmuhurtas: list[DurmuhurtaWindow]
    varjyam_windows: list[VarjyamWindow]
    amrita_windows: list[AmritaKalaWindow]
    kala_windows: list[AmritaKalaWindow]
    overall_quality: MuhurtaQuality


@dataclass
class MuhurtaInputs:
    """Input parameters for advanced muhurta calculation."""

    date_value: datetime
    sunrise: datetime
    sunset: datetime
    tithi: int
    nakshatra: int
    tithi_end_time: datetime


def _get_muhurta_index(time: datetime, sunrise: datetime) -> int:
    """Get muhurta index (1-30) for a given time."""
    elapsed_minutes = (time - sunrise).total_seconds() / 60.0
    index = int(elapsed_minutes / MINUTES_PER_MUHURTA) + 1
    return max(1, min(30, index))


def _add_minutes(dt: datetime, minutes: float) -> datetime:
    """Add minutes to a datetime."""
    return dt + datetime_module.timedelta(minutes=minutes)


def get_durmuhurtas(
    sunrise: datetime,
) -> list[DurmuhurtaWindow]:
    """Calculate Durmuhurta windows (inauspicious muhurtas).

    Args:
        sunrise: Sunrise time for the date.

    Returns:
        List of DurmuhurtaWindow.

    """
    durmuhurtas: list[DurmuhurtaWindow] = []

    for index in DURMUHURTA_INDICES:
        start_minutes = (index - 1) * MINUTES_PER_MUHURTA
        end_minutes = index * MINUTES_PER_MUHURTA

        start_time = _add_minutes(sunrise, start_minutes)
        end_time = _add_minutes(sunrise, end_minutes)

        window = TimeWindow(
            start=start_time,
            end=end_time,
            duration_minutes=MINUTES_PER_MUHURTA,
        )

        description = f"Durmuhurta {index} - avoid important activities."

        durmuhurtas.append(
            DurmuhurtaWindow(
                window=window,
                muhurta_index=index,
                description=description,
            )
        )

    return durmuhurtas


def get_varjyam_windows(
    tithi: int,
    nakshatra: int,
    tithi_end_time: datetime,
) -> list[VarjyamWindow]:
    """Calculate Varjyam (void) timings.

    Varjyam is calculated from the end of tithi backwards.

    Args:
        tithi: Current tithi (1-30).
        nakshatra: Current nakshatra (1-27).
        tithi_end_time: Time when tithi ends.

    Returns:
        List of VarjyamWindow.

    """
    # Varjyam duration in ghatis (1 ghati = 24 minutes)
    varjyam_ghatis_map = {
        1: 3,
        2: 4,
        3: 2,
        4: 5,
        5: 7,
        6: 3,
        7: 1,
        8: 4,
        9: 5,
        10: 2,
        11: 6,
        12: 4,
        13: 3,
        14: 2,
        15: 1,
        16: 3,
        17: 4,
        18: 2,
        19: 5,
        20: 7,
        21: 3,
        22: 1,
        23: 4,
        24: 5,
        25: 2,
        26: 6,
        27: 4,
        28: 3,
        29: 2,
        30: 1,
    }

    varjyam_ghatis = varjyam_ghatis_map.get(tithi, 3)
    varjyam_minutes = varjyam_ghatis * 24.0

    start_time = tithi_end_time - datetime_module.timedelta(minutes=varjyam_minutes)
    end_time = tithi_end_time

    window = TimeWindow(
        start=start_time,
        end=end_time,
        duration_minutes=varjyam_minutes,
    )

    description = f"Varjyam for Tithi {tithi} - void period, avoid new beginnings."

    return [
        VarjyamWindow(
            window=window,
            tithi=tithi,
            nakshatra=nakshatra,
            description=description,
        )
    ]


def get_amrita_kala_windows(
    weekday: int,
    nakshatra: int,
    sunrise: datetime,
    sunset: datetime,
) -> tuple[list[AmritaKalaWindow], list[AmritaKalaWindow]]:
    """Calculate Amrita Kala (auspicious) and Kala (inauspicious) windows.

    Args:
        weekday: Weekday index (0=Sunday, 6=Saturday).
        nakshatra: Current nakshatra (1-27).
        sunrise: Sunrise time.
        sunset: Sunset time.

    Returns:
        Tuple of (amrita_windows, kala_windows).

    """
    # Simplified Amrita Kala calculation (weekday-nakshatra based)
    # This is a placeholder - full calculation needs ephemeris data
    amrita_windows: list[AmritaKalaWindow] = []
    kala_windows: list[AmritaKalaWindow] = []

    day_length = (sunset - sunrise).total_seconds() / 60.0
    segment_duration = day_length / 8.0

    # Example: Amrita on specific weekday-nakshatra combinations
    # Sunday with Ashwini (1), Rohini (4), etc.
    amrita_combinations = {
        0: [1, 4, 7, 10, 13, 16, 19, 22, 25],  # Sunday
        1: [2, 5, 8, 11, 14, 17, 20, 23, 26],  # Monday
        2: [3, 6, 9, 12, 15, 18, 21, 24, 27],  # Tuesday
        3: [1, 4, 7, 10, 13, 16, 19, 22, 25],  # Wednesday
        4: [2, 5, 8, 11, 14, 17, 20, 23, 26],  # Thursday
        5: [3, 6, 9, 12, 15, 18, 21, 24, 27],  # Friday
        6: [1, 4, 7, 10, 13, 16, 19, 22, 25],  # Saturday
    }

    if nakshatra in amrita_combinations.get(weekday, []):
        # Amrita window (example: 3rd segment of day)
        start_time = _add_minutes(sunrise, 2 * segment_duration)
        end_time = _add_minutes(sunrise, 3 * segment_duration)

        window = TimeWindow(
            start=start_time,
            end=end_time,
            duration_minutes=segment_duration,
        )

        amrita_windows.append(
            AmritaKalaWindow(
                window=window,
                quality="amrita",
                weekday=weekday,
                nakshatra=nakshatra,
                description="Amrita Kala - nectar time, highly auspicious.",
            )
        )
    else:
        # Kala window (inauspicious)
        start_time = _add_minutes(sunrise, 4 * segment_duration)
        end_time = _add_minutes(sunrise, 5 * segment_duration)

        window = TimeWindow(
            start=start_time,
            end=end_time,
            duration_minutes=segment_duration,
        )

        kala_windows.append(
            AmritaKalaWindow(
                window=window,
                quality="kala",
                weekday=weekday,
                nakshatra=nakshatra,
                description="Kala - death time, avoid important activities.",
            )
        )

    return amrita_windows, kala_windows


def calculate_advanced_muhurta(
    inputs: MuhurtaInputs,
) -> AdvancedMuhurtaReport:
    """Calculate complete advanced muhurta analysis.

    Args:
        inputs: MuhurtaInputs with all required parameters.

    Returns:
        AdvancedMuhurtaReport with all timing windows.

    """
    weekday = inputs.date_value.weekday()
    weekday_vedic = (weekday + 1) % 7  # Convert to Vedic (0=Sunday)

    durmuhurtas = get_durmuhurtas(inputs.sunrise)
    varjyam = get_varjyam_windows(inputs.tithi, inputs.nakshatra, inputs.tithi_end_time)
    amrita, kala = get_amrita_kala_windows(weekday_vedic, inputs.nakshatra, inputs.sunrise, inputs.sunset)

    # Determine overall quality
    overall_quality = MuhurtaQuality.AVERAGE
    if len(amrita) > 0:
        overall_quality = MuhurtaQuality.EXCELLENT
    elif len(kala) > 0 or len(durmuhurtas) > 2:  # noqa: PLR2004
        overall_quality = MuhurtaQuality.POOR

    return AdvancedMuhurtaReport(
        date=inputs.date_value,
        durmuhurtas=durmuhurtas,
        varjyam_windows=varjyam,
        amrita_windows=amrita,
        kala_windows=kala,
        overall_quality=overall_quality,
    )
