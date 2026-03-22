# Astrological Data Loader Utility

## Overview

The `AstroDataLoader` is a comprehensive utility class that provides centralized access to all astrological reference data stored in JSON files within the `ndastro_api/resources/data` directory. It implements a singleton pattern with lazy loading and caching for optimal performance.

## Features

- **Singleton Pattern**: Only one instance exists throughout the application lifecycle
- **Lazy Loading**: Data files are loaded only when requested
- **Caching**: All loaded data is cached in memory to avoid repeated file reads
- **Type Safety**: Consistent return types with proper typing hints
- **Comprehensive Coverage**: Access to 30+ different astrological data files
- **Convenience Methods**: Simple query methods to find specific data by name, code, or number
- **Binary File Support**: Access paths to ephemeris (BSP) and database files

## Installation

The data loader is part of the core utilities and is automatically available when you import from `ndastro_api.core.utils`.

## Quick Start

### Basic Usage

```python
from ndastro_api.core.utils import astro_data, get_planets

# Method 1: Using convenience functions
planets = get_planets()
print(f"Found {len(planets)} planets")

# Method 2: Using the singleton instance
nakshatras = astro_data.get_nakshatras()
print(f"Found {len(nakshatras)} nakshatras")

# Method 3: Direct instantiation (returns same singleton)
from ndastro_api.core.utils.data_loader import AstroDataLoader
loader = AstroDataLoader()
rasis = loader.get_rasis()
```

## Available Data

### Core Astrological Data

| Method | Description | Returns |
|--------|-------------|---------|
| `get_planets()` | All planet data | List of planet objects |
| `get_nakshatras()` | All 27 nakshatras | List of nakshatra objects |
| `get_rasis()` | All 12 zodiac signs | List of rasi objects |
| `get_houses()` | All 12 house meanings | List of house objects |
| `get_yogas()` | All 27 nitya yogas | List of yoga objects |

### Panchanga Elements

| Method | Description | Returns |
|--------|-------------|---------|
| `get_tithis()` | All 30 lunar days | List of tithi objects |
| `get_karanas()` | All 11 karanas | List of karana objects |
| `get_varas()` | All 7 weekdays | List of vara objects |

### Dasha Systems

| Method | Description | Returns |
|--------|-------------|---------|
| `get_dasha_systems()` | All dasha systems | List of dasha system objects |
| `get_dasha_period_guide()` | Dasha interpretation guide | Dasha guide data |

### Advanced Techniques

| Method | Description | Returns |
|--------|-------------|---------|
| `get_divisional_charts()` | All varga charts | List of divisional chart configs |
| `get_ashtakavarga()` | Ashtakavarga system | Ashtakavarga data |
| `get_avasthas()` | Planetary states | Avastha data |
| `get_upagrahas()` | Sub-planets | List of upagraha objects |
| `get_special_lagnas()` | Special ascendants | List of special lagna objects |
| `get_tarabala()` | Birth star compatibility | Tarabala data |

### Planetary Yogas & Combinations

| Method | Description | Returns |
|--------|-------------|---------|
| `get_planetary_yogas()` | Planetary combinations | List of yoga configurations |
| `get_yogas_deep_dive()` | Detailed yoga analysis | Comprehensive yoga data |

### Predictive & Specialized Branches

| Method | Description | Returns |
|--------|-------------|---------|
| `get_predictive_techniques()` | Various prediction methods | Predictive technique data |
| `get_muhurta_electional()` | Electional astrology | Muhurta data |
| `get_prasna_horary()` | Horary astrology | Prasna data |
| `get_nadi_astrology()` | Nadi astrology techniques | Nadi data |
| `get_medical_astrology()` | Medical astrology | Medical astrology data |

### Analysis & Counseling

| Method | Description | Returns |
|--------|-------------|---------|
| `get_compatibility_analysis()` | Compatibility techniques | Compatibility data |
| `get_relationship_synastry()` | Relationship analysis | Synastry data |
| `get_career_counseling()` | Career guidance data | Career counseling data |
| `get_wealth_timing()` | Wealth analysis | Wealth timing data |
| `get_spiritual_progress()` | Spiritual indicators | Spiritual progress data |

### Remedial Measures

| Method | Description | Returns |
|--------|-------------|---------|
| `get_remedial_measures()` | Comprehensive remedies | Remedial measures data |

### Binary Files

| Method | Description | Returns |
|--------|-------------|---------|
| `get_ephemeris_file_path()` | DE440s ephemeris file path | Path object |
| `get_database_file_path()` | Local database file path | Path object |

## Query Methods

Most data types support convenient query methods:

### By Code
```python
# Get planet by code
sun = astro_data.get_planet_by_code("SU")
print(sun['name'])  # "Sun"
```

### By Name
```python
# Get rasi by name (case-insensitive)
aries = astro_data.get_rasi_by_name("Aries")
print(aries['ruler'])  # "Mars"

# Get nakshatra by name
ashwini = astro_data.get_nakshatra_by_name("Ashwini")
print(ashwini['rulingPlanet'])  # "Ketu"
```

### By Number
```python
# Get house by number
first_house = astro_data.get_house_by_number(1)
print(first_house['description'])  # "The Ascendant (Lagna)"

# Get nakshatra by number (1-27)
bharani = astro_data.get_nakshatra_by_number(2)
print(bharani['name'])  # "Bharani"
```

## Practical Examples

### Example 1: Birth Chart Analysis

```python
from ndastro_api.core.utils import astro_data

# Get birth nakshatra
birth_nakshatra = astro_data.get_nakshatra_by_number(1)  # Ashwini
print(f"Birth Nakshatra: {birth_nakshatra['name']}")
print(f"Ruling Planet: {birth_nakshatra['rulingPlanet']}")

# Get ruling planet details
ruling_planet = astro_data.get_planet_by_name(birth_nakshatra['rulingPlanet'])
print(f"Gemstone: {ruling_planet['gemstone']}")
print(f"Color: {ruling_planet['color']}")

# Get dasha information
dasha_system = astro_data.get_dasha_system_by_name("Vimshottari Dasha")
periods = dasha_system['periods']
current_period = next(p for p in periods if p['planet'] == birth_nakshatra['rulingPlanet'])
print(f"Mahadasha Duration: {current_period['years']} years")
```

### Example 2: Checking Planetary Positions

```python
# Check if a planet is exalted in a sign
mars = astro_data.get_planet_by_name("Mars")
exaltation_sign = mars['exaltation']['sign']
print(f"Mars is exalted in {exaltation_sign}")

# Get the sign details
sign = astro_data.get_rasi_by_name(exaltation_sign)
print(f"Sign ruler: {sign['ruler']}")
print(f"Sign element: {sign['elementPanchamahabhuta']}")
```

### Example 3: House Analysis

```python
# Analyze multiple houses
for house_num in [1, 4, 7, 10]:  # Kendra houses
    house = astro_data.get_house_by_number(house_num)
    print(f"{house['name']}: {house['description']}")
    print(f"  Keywords: {', '.join(house['keywords'][:3])}")
    print(f"  Kendra: {house['kendra']}")
```

### Example 4: Compatibility Check

```python
# Get compatibility data
compatibility = astro_data.get_compatibility_analysis()

# Get tarabala for birth star compatibility
tarabala = astro_data.get_tarabala()

# Analyze relationship synastry
synastry = astro_data.get_relationship_synastry()
```

### Example 5: Finding Remedies

```python
# Get remedial measures
remedies = astro_data.get_remedial_measures()

# Get planet-specific remedy
planet = astro_data.get_planet_by_name("Saturn")
print(f"Gemstone: {planet['gemstone']}")
print(f"Metal: {planet['metal']}")
print(f"Day: {planet['day']}")
```

## Advanced Features

### Preloading All Data

For applications that need all data upfront:

```python
from ndastro_api.core.utils import astro_data

# Preload all JSON files into cache
astro_data.preload_all()
```

### Cache Management

```python
# Clear cache to force reload
astro_data.clear_cache()

# Data will be reloaded on next access
planets = astro_data.get_planets()
```

### Listing Available Files

```python
# Get list of all data files
files = astro_data.get_all_data_files()
print(f"Total data files: {len(files)}")
for file in files:
    print(f"  - {file}")
```

## Data Structure Examples

### Planet Object
```json
{
  "name": "Sun",
  "code": "SU",
  "sanskritName": "Surya",
  "elementPanchamahabhuta": "Fire",
  "gender": "Male",
  "nature": "Malefic",
  "gemstone": "Ruby",
  "ownSigns": ["Leo"],
  "exaltation": {
    "sign": "Aries",
    "deepExaltationDegree": 10.0
  }
}
```

### Nakshatra Object
```json
{
  "name": "Ashwini",
  "code": "N01",
  "number": 1,
  "rulingPlanet": "Ketu",
  "rulingDeity": "Ashwini Kumaras",
  "symbol": "Horse's Head",
  "startDegree": 0.0,
  "endDegree": 13.333333,
  "rasi": "Aries"
}
```

### Rasi Object
```json
{
  "name": "Aries",
  "code": "AR",
  "number": 1,
  "elementPanchamahabhuta": "Fire",
  "quality": "Movable",
  "ruler": "Mars",
  "exaltedPlanet": "Sun"
}
```

## Performance Considerations

1. **First Access**: Each data file is loaded from disk only once
2. **Subsequent Access**: Data is served from memory cache
3. **Memory Usage**: All JSON files total approximately 2-3 MB when loaded
4. **Singleton Instance**: Shared across all parts of the application
5. **Thread Safety**: Cache is shared but read-only after loading

## Error Handling

```python
try:
    planet = astro_data.get_planet_by_code("XX")
    if planet is None:
        print("Planet not found")
except FileNotFoundError as e:
    print(f"Data file missing: {e}")
```

## Testing

Run the example file to verify all data loads correctly:

```bash
cd ndastro-api
poetry run python -m ndastro_api.examples.data_loader_examples
```

## Integration with API Endpoints

Example of using the data loader in FastAPI endpoints:

```python
from fastapi import APIRouter
from ndastro_api.core.utils import astro_data

router = APIRouter()

@router.get("/planets")
async def list_planets():
    """Get all planets"""
    return astro_data.get_planets()

@router.get("/planets/{code}")
async def get_planet(code: str):
    """Get planet by code"""
    planet = astro_data.get_planet_by_code(code.upper())
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")
    return planet

@router.get("/nakshatras/{number}")
async def get_nakshatra(number: int):
    """Get nakshatra by number"""
    nakshatra = astro_data.get_nakshatra_by_number(number)
    if not nakshatra:
        raise HTTPException(status_code=404, detail="Nakshatra not found")
    return nakshatra
```

## Contributing

When adding new data files:

1. Place JSON file in `ndastro_api/resources/data/`
2. Add corresponding method to `AstroDataLoader` class
3. Add filename to `get_all_data_files()` list
4. Update this documentation

## License

This utility is part of the ndastro-api project.
