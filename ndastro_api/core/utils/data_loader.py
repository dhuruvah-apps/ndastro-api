"""Data Loader Utility for Astrological Resources.

Provides centralized access to all JSON data files in resources/data directory
"""

import contextlib
import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import TypeAdapter

from ndastro_api.core.models.astro_system import (
    DashaSystem,
    DivisionalChart,
    House,
    Karana,
    Nakshatra,
    Planet,
    PlanetaryYoga,
    Rasi,
    SpecialLagna,
    Tithi,
    Upagraha,
    Vara,
    Yoga,
)

T = TypeVar("T")


def _camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case.

    Args:
        name: camelCase string

    Returns:
        snake_case string

    """
    result = []
    for i, char in enumerate(name):
        # Add underscore before uppercase letter
        if char.isupper() and i > 0 and (name[i - 1].islower() or (i < len(name) - 1 and name[i + 1].islower())):
            result.append("_")
        result.append(char.lower())
    return "".join(result)


def _json_object_hook(obj: dict[str, Any]) -> dict[str, Any]:
    """Convert camelCase keys to snake_case during JSON deserialization.

    This object_hook is called for every JSON object loaded, converting
    keys from camelCase (in JSON) to snake_case (for Python dataclasses).

    Args:
        obj: Dictionary object from JSON

    Returns:
        Dictionary with snake_case keys

    """
    return {_camel_to_snake(k): v for k, v in obj.items()}


class AstroDataLoader:
    """Utility class to load and provide access to astrological data files.

    All data is loaded lazily and cached for performance.
    """

    _instance = None

    def __new__(cls) -> "AstroDataLoader":
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the data loader with the base data directory path."""
        if not hasattr(self, "initialized"):
            self.data_dir = Path(__file__).parent.parent.parent / "resources" / "data"
            self._data_cache: dict[str, Any] = {}  # Cache for raw JSON data
            self._model_cache: dict[str, list[Any]] = {}  # Cache for parsed Pydantic models
            self._adapter_cache: dict[type, TypeAdapter] = {}  # Cache for TypeAdapter instances
            self.initialized = True

    def _load_json(self, filename: str) -> dict[str, Any] | list[Any]:
        """Load a JSON file from the data directory.

        Uses custom object_hook to convert camelCase keys to snake_case
        during JSON deserialization for optimal performance.

        Args:
            filename: Name of the JSON file to load

        Returns:
            Parsed JSON data (list or dict) with snake_case keys

        """
        if filename in self._data_cache:
            return self._data_cache[filename]

        file_path = self.data_dir / filename
        if not file_path.exists():
            msg = f"Data file not found: {filename}"
            raise FileNotFoundError(msg)

        with file_path.open(encoding="utf-8") as f:
            data = json.load(f, object_hook=_json_object_hook)

        self._data_cache[filename] = data
        return data

    def _load_and_parse(self, filename: str, model: type[T]) -> list[T]:
        """Load JSON file and parse into Pydantic dataclass models.

        Uses caching for both parsed models and TypeAdapter instances
        to avoid repeated overhead.

        Args:
            filename: Name of the JSON file to load
            model: Pydantic dataclass model class to parse into

        Returns:
            List of parsed model instances.

        """
        cache_key = f"{filename}:{model.__name__}"

        # Return cached parsed models if available
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]  # type: ignore[return-value]

        # Load raw JSON data
        data = self._load_json(filename)

        # Get or create TypeAdapter for this model (reuse across calls)
        if model not in self._adapter_cache:
            self._adapter_cache[model] = TypeAdapter(model)
        adapter = self._adapter_cache[model]

        # Parse and cache the results
        parsed_data = [adapter.validate_python(item) for item in data]  # type: ignore[arg-type]
        self._model_cache[cache_key] = parsed_data

        return parsed_data  # type: ignore[return-value]

    # Planet Data
    def get_planets(self) -> list[Planet]:
        """Get all planet data."""
        return self._load_and_parse("planets.json", Planet)

    def get_planet_by_code(self, code: str) -> Planet | None:
        """Get planet data by planet code (e.g., 'SU' for Sun)."""
        planets = self.get_planets()
        return next((p for p in planets if p.code == code), None)

    def get_planet_by_astronomical_code(self, astronomical_code: str) -> Planet | None:
        """Get planet data by astronomical code (e.g., 'sun' for Sun)."""
        planets = self.get_planets()
        return next((p for p in planets if p.astronomical_code == astronomical_code), None)

    def get_planet_by_name(self, name: str, longitude: float = 0, latitude: float = 0) -> Planet | None:
        """Get planet data by planet name."""
        planets = self.get_planets()
        return next((p for p in planets if p.name.lower() == name.lower()), None)

    # Nakshatra Data
    def get_nakshatras(self) -> list[Nakshatra]:
        """Get all nakshatra data."""
        return self._load_and_parse("nakshatras.json", Nakshatra)

    def get_nakshatra_by_number(self, number: int) -> Nakshatra | None:
        """Get nakshatra data by number (1-27)."""
        nakshatras = self.get_nakshatras()
        return next((n for n in nakshatras if n.number == number), None)

    def get_nakshatra_by_name(self, name: str) -> Nakshatra | None:
        """Get nakshatra data by name."""
        nakshatras = self.get_nakshatras()
        return next((n for n in nakshatras if n.name.lower() == name.lower()), None)

    # Rasi (Zodiac Sign) Data
    def get_rasis(self) -> list[Rasi]:
        """Get all rasi (zodiac sign) data."""
        return self._load_and_parse("rasis.json", Rasi)

    def get_rasi_by_number(self, number: int) -> Rasi | None:
        """Get rasi data by number (1-12)."""
        rasis = self.get_rasis()
        return next((r for r in rasis if r.number == number), None)

    def get_rasi_by_name(self, name: str) -> Rasi | None:
        """Get rasi data by name."""
        rasis = self.get_rasis()
        return next((r for r in rasis if r.name.lower() == name.lower()), None)

    # House Data
    def get_houses(self) -> list[House]:
        """Get all house data."""
        return self._load_and_parse("houses.json", House)

    def get_house_by_number(self, number: int) -> House | None:
        """Get house data by number (1-12)."""
        houses = self.get_houses()
        return next((h for h in houses if h.number == number), None)

    # Yoga Data
    def get_yogas(self) -> list[Yoga]:
        """Get all yoga data."""
        return self._load_and_parse("yogas.json", Yoga)

    def get_yoga_by_number(self, number: int) -> Yoga | None:
        """Get yoga data by number."""
        yogas = self.get_yogas()
        return next((y for y in yogas if y.number == number), None)

    def get_yoga_by_name(self, name: str) -> Yoga | None:
        """Get yoga data by name."""
        yogas = self.get_yogas()
        return next((y for y in yogas if y.name.lower() == name.lower()), None)

    # Planetary Yogas
    def get_planetary_yogas(self) -> list[PlanetaryYoga]:
        """Get all planetary yoga configurations."""
        return self._load_and_parse("planetary_yogas.json", PlanetaryYoga)

    def get_planetary_yoga_by_name(self, name: str) -> PlanetaryYoga | None:
        """Get planetary yoga by name."""
        yogas = self.get_planetary_yogas()
        return next((y for y in yogas if y.name.lower() == name.lower()), None)

    # Yogas Deep Dive
    def get_yogas_deep_dive(self) -> dict[str, Any] | list[Any]:
        """Get detailed yoga analysis data."""
        return self._load_json("yogas_deep_dive.json")

    # Dasha Systems
    def get_dasha_systems(self) -> list[DashaSystem]:
        """Get all dasha system data."""
        return self._load_and_parse("dasha_systems.json", DashaSystem)

    def get_dasha_system_by_name(self, name: str) -> DashaSystem | None:
        """Get dasha system by name."""
        systems = self.get_dasha_systems()
        return next((d for d in systems if d.name.lower() == name.lower()), None)

    # Dasha Period Guide
    def get_dasha_period_guide(self) -> dict[str, Any] | list[Any]:
        """Get dasha period interpretation guide."""
        return self._load_json("dasha_period_guide.json")

    # Tithi Data
    def get_tithis(self) -> list[Tithi]:
        """Get all tithi (lunar day) data."""
        return self._load_and_parse("tithis.json", Tithi)

    def get_tithi_by_number(self, number: int) -> Tithi | None:
        """Get tithi data by number (1-30)."""
        tithis = self.get_tithis()
        return next((t for t in tithis if t.number == number), None)

    # Karana Data
    def get_karanas(self) -> list[Karana]:
        """Get all karana data."""
        return self._load_and_parse("karanas.json", Karana)

    def get_karana_by_number(self, number: int) -> Karana | None:
        """Get karana data by number."""
        karanas = self.get_karanas()
        return next((k for k in karanas if k.number == number), None)

    # Vara (Weekday) Data
    def get_varas(self) -> list[Vara]:
        """Get all vara (weekday) data."""
        return self._load_and_parse("varas.json", Vara)

    def get_vara_by_number(self, number: int) -> Vara | None:
        """Get vara data by number (1-7)."""
        varas = self.get_varas()
        return next((v for v in varas if v.number == number), None)

    # Divisional Charts
    def get_divisional_charts(self) -> list[DivisionalChart]:
        """Get all divisional chart (varga) data."""
        return self._load_and_parse("divisional_charts.json", DivisionalChart)

    def get_divisional_chart_by_name(self, name: str) -> DivisionalChart | None:
        """Get divisional chart by name."""
        charts = self.get_divisional_charts()
        return next((c for c in charts if c.name.lower() == name.lower()), None)

    # Ashtakavarga
    def get_ashtakavarga(self) -> dict[str, Any] | list[Any]:
        """Get ashtakavarga system data."""
        return self._load_json("ashtakavarga.json")

    # Avasthas
    def get_avasthas(self) -> dict[str, Any] | list[Any]:
        """Get planetary avastha (state) data."""
        return self._load_json("avasthas.json")

    # Upagrahas
    def get_upagrahas(self) -> list[Upagraha]:
        """Get all upagraha (sub-planet) data."""
        return self._load_and_parse("upagrahas.json", Upagraha)

    def get_upagraha_by_name(self, name: str) -> Upagraha | None:
        """Get upagraha by name."""
        upagrahas = self.get_upagrahas()
        return next((u for u in upagrahas if u.name.lower() == name.lower()), None)

    # Special Lagnas
    def get_special_lagnas(self) -> list[SpecialLagna]:
        """Get all special lagna data."""
        return self._load_and_parse("special_lagnas.json", SpecialLagna)

    def get_special_lagna_by_name(self, name: str) -> SpecialLagna | None:
        """Get special lagna by name."""
        lagnas = self.get_special_lagnas()
        return next((lagna for lagna in lagnas if lagna.name.lower() == name.lower()), None)

    # Tarabala
    def get_tarabala(self) -> dict[str, Any] | list[Any]:
        """Get tarabala (birth star compatibility) data."""
        return self._load_json("tarabala.json")

    # Predictive Techniques
    def get_predictive_techniques(self) -> dict[str, Any] | list[Any]:
        """Get predictive techniques data."""
        return self._load_json("predictive_techniques.json")

    # Muhurta (Electional Astrology)
    def get_muhurta_electional(self) -> dict[str, Any] | list[Any]:
        """Get muhurta and electional astrology data."""
        return self._load_json("muhurta_electional.json")

    # Prasna (Horary Astrology)
    def get_prasna_horary(self) -> dict[str, Any] | list[Any]:
        """Get prasna (horary) astrology data."""
        return self._load_json("prasna_horary.json")

    # Nadi Astrology
    def get_nadi_astrology(self) -> dict[str, Any] | list[Any]:
        """Get nadi astrology data."""
        return self._load_json("nadi_astrology.json")

    # Medical Astrology
    def get_medical_astrology(self) -> dict[str, Any] | list[Any]:
        """Get medical astrology data."""
        return self._load_json("medical_astrology.json")

    # Remedial Measures
    def get_remedial_measures(self) -> dict[str, Any] | list[Any]:
        """Get comprehensive remedial measures data."""
        return self._load_json("remedial_measures_comprehensive.json")

    # Compatibility Analysis
    def get_compatibility_analysis(self) -> dict[str, Any] | list[Any]:
        """Get compatibility analysis data."""
        return self._load_json("compatibility_analysis.json")

    # Relationship Synastry
    def get_relationship_synastry(self) -> dict[str, Any] | list[Any]:
        """Get relationship synastry data."""
        return self._load_json("relationship_synastry.json")

    # Career Counseling
    def get_career_counseling(self) -> dict[str, Any] | list[Any]:
        """Get career counseling astrological data."""
        return self._load_json("career_counseling.json")

    # Wealth Timing
    def get_wealth_timing(self) -> dict[str, Any] | list[Any]:
        """Get wealth timing analysis data."""
        return self._load_json("wealth_timing.json")

    # Spiritual Progress
    def get_spiritual_progress(self) -> dict[str, Any] | list[Any]:
        """Get spiritual progress indicators data."""
        return self._load_json("spiritual_progress.json")

    # Binary Data Files
    def get_ephemeris_file_path(self) -> Path:
        """Get path to DE440s ephemeris binary file."""
        return self.data_dir / "de440s.bsp"

    def get_database_file_path(self) -> Path:
        """Get path to the local database file."""
        return self.data_dir / "ndastro_app.db"

    # Utility Methods
    def clear_cache(self) -> None:
        """Clear all caches to force reload of all files."""
        self._data_cache.clear()
        self._model_cache.clear()
        # Keep adapter cache as TypeAdapters don't hold data, just schema

    def get_all_data_files(self) -> list[str]:
        """Get list of all available JSON data files."""
        return [
            "planets.json",
            "nakshatras.json",
            "rasis.json",
            "houses.json",
            "yogas.json",
            "planetary_yogas.json",
            "yogas_deep_dive.json",
            "dasha_systems.json",
            "dasha_period_guide.json",
            "tithis.json",
            "karanas.json",
            "varas.json",
            "divisional_charts.json",
            "ashtakavarga.json",
            "avasthas.json",
            "upagrahas.json",
            "special_lagnas.json",
            "tarabala.json",
            "predictive_techniques.json",
            "muhurta_electional.json",
            "prasna_horary.json",
            "nadi_astrology.json",
            "medical_astrology.json",
            "remedial_measures_comprehensive.json",
            "compatibility_analysis.json",
            "relationship_synastry.json",
            "career_counseling.json",
            "wealth_timing.json",
            "spiritual_progress.json",
        ]

    def preload_all(self) -> None:
        """Preload all JSON data files into cache."""
        for filename in self.get_all_data_files():
            with contextlib.suppress(FileNotFoundError):
                self._load_json(filename)


# Global singleton instance
astro_data = AstroDataLoader()


# Convenience functions for direct access
def get_planets() -> list[Planet]:
    """Get all planet data."""
    return astro_data.get_planets()


def get_nakshatras() -> list[Nakshatra]:
    """Get all nakshatra data."""
    return astro_data.get_nakshatras()


def get_rasis() -> list[Rasi]:
    """Get all rasi data."""
    return astro_data.get_rasis()


def get_houses() -> list[House]:
    """Get all house data."""
    return astro_data.get_houses()


def get_yogas() -> list[Yoga]:
    """Get all yoga data."""
    return astro_data.get_yogas()


def get_dasha_systems() -> list[DashaSystem]:
    """Get all dasha system data."""
    return astro_data.get_dasha_systems()
