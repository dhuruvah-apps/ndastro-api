# Data Loader Quick Reference

## Import
```python
from ndastro_api.core.utils import astro_data
```

## Most Common Operations

### Get All Data
```python
planets = astro_data.get_planets()              # All 10 planets
nakshatras = astro_data.get_nakshatras()        # All 27 nakshatras
rasis = astro_data.get_rasis()                  # All 12 signs
houses = astro_data.get_houses()                # All 12 houses
tithis = astro_data.get_tithis()                # All 30 tithis
yogas = astro_data.get_yogas()                  # All 27 yogas
```

### Find by Code/Name/Number
```python
# By Code
sun = astro_data.get_planet_by_code("SU")
moon = astro_data.get_planet_by_code("MO")

# By Name (case-insensitive)
mars = astro_data.get_planet_by_name("Mars")
aries = astro_data.get_rasi_by_name("aries")
ashwini = astro_data.get_nakshatra_by_name("Ashwini")

# By Number
nak_1 = astro_data.get_nakshatra_by_number(1)     # Ashwini
house_1 = astro_data.get_house_by_number(1)       # First House
rasi_1 = astro_data.get_rasi_by_number(1)         # Aries
```

### Dasha Systems
```python
all_dashas = astro_data.get_dasha_systems()
vimshottari = astro_data.get_dasha_system_by_name("Vimshottari Dasha")
guide = astro_data.get_dasha_period_guide()
```

### Specialized Data
```python
# Predictive
predictive = astro_data.get_predictive_techniques()
muhurta = astro_data.get_muhurta_electional()
prasna = astro_data.get_prasna_horary()

# Analysis
compatibility = astro_data.get_compatibility_analysis()
synastry = astro_data.get_relationship_synastry()
career = astro_data.get_career_counseling()
wealth = astro_data.get_wealth_timing()

# Remedies
remedies = astro_data.get_remedial_measures()

# Advanced
ashtakavarga = astro_data.get_ashtakavarga()
avasthas = astro_data.get_avasthas()
upagrahas = astro_data.get_upagrahas()
special_lagnas = astro_data.get_special_lagnas()
```

### Binary Files
```python
ephemeris_path = astro_data.get_ephemeris_file_path()
db_path = astro_data.get_database_file_path()
```

### Utility
```python
# List all available files
files = astro_data.get_all_data_files()

# Preload everything
astro_data.preload_all()

# Clear cache
astro_data.clear_cache()
```

## Common Patterns

### Planet Info
```python
planet = astro_data.get_planet_by_name("Jupiter")
print(f"{planet['name']} ({planet['sanskritName']})")
print(f"Nature: {planet['nature']}")
print(f"Gemstone: {planet['gemstone']}")
print(f"Exalted in: {planet['exaltation']['sign']}")
```

### Nakshatra Lookup
```python
nak = astro_data.get_nakshatra_by_number(10)
print(f"Nakshatra: {nak['name']}")
print(f"Lord: {nak['rulingPlanet']}")
print(f"Deity: {nak['rulingDeity']}")
print(f"Range: {nak['startDegree']}° - {nak['endDegree']}°")
```

### House Meanings
```python
house = astro_data.get_house_by_number(7)
print(f"{house['name']}: {house['description']}")
print(f"Keywords: {', '.join(house['keywords'])}")
print(f"Represents: {', '.join(house['represents'][:5])}")
```

### Dasha Analysis
```python
dasha = astro_data.get_dasha_system_by_name("Vimshottari Dasha")
for period in dasha['periods']:
    print(f"{period['planet']}: {period['years']} years")
    print(f"  Nature: {period['nature']}")
```

## API Endpoint Example
```python
from fastapi import APIRouter, HTTPException
from ndastro_api.core.utils import astro_data

router = APIRouter(prefix="/astro-data", tags=["Astro Data"])

@router.get("/planets")
async def list_planets():
    return astro_data.get_planets()

@router.get("/planets/{code}")
async def get_planet(code: str):
    planet = astro_data.get_planet_by_code(code.upper())
    if not planet:
        raise HTTPException(404, "Planet not found")
    return planet

@router.get("/nakshatras/{number}")
async def get_nakshatra(number: int):
    if not 1 <= number <= 27:
        raise HTTPException(400, "Number must be 1-27")
    return astro_data.get_nakshatra_by_number(number)
```

## Data File Mapping

| File | Method | Type |
|------|--------|------|
| planets.json | `get_planets()` | List |
| nakshatras.json | `get_nakshatras()` | List |
| rasis.json | `get_rasis()` | List |
| houses.json | `get_houses()` | List |
| yogas.json | `get_yogas()` | List |
| planetary_yogas.json | `get_planetary_yogas()` | List |
| dasha_systems.json | `get_dasha_systems()` | List |
| tithis.json | `get_tithis()` | List |
| karanas.json | `get_karanas()` | List |
| varas.json | `get_varas()` | List |
| divisional_charts.json | `get_divisional_charts()` | List |
| upagrahas.json | `get_upagrahas()` | List |
| special_lagnas.json | `get_special_lagnas()` | List |
| ashtakavarga.json | `get_ashtakavarga()` | Dict |
| avasthas.json | `get_avasthas()` | Dict |
| tarabala.json | `get_tarabala()` | Dict |
| predictive_techniques.json | `get_predictive_techniques()` | Dict |
| muhurta_electional.json | `get_muhurta_electional()` | Dict |
| prasna_horary.json | `get_prasna_horary()` | Dict |
| nadi_astrology.json | `get_nadi_astrology()` | Dict |
| medical_astrology.json | `get_medical_astrology()` | Dict |
| compatibility_analysis.json | `get_compatibility_analysis()` | Dict |
| relationship_synastry.json | `get_relationship_synastry()` | Dict |
| career_counseling.json | `get_career_counseling()` | Dict |
| wealth_timing.json | `get_wealth_timing()` | Dict |
| spiritual_progress.json | `get_spiritual_progress()` | Dict |
| remedial_measures_comprehensive.json | `get_remedial_measures()` | Dict |
| dasha_period_guide.json | `get_dasha_period_guide()` | Dict |
| yogas_deep_dive.json | `get_yogas_deep_dive()` | Dict |

## Performance Tips

1. **Singleton Reuse**: Always use `astro_data` (singleton instance)
2. **Preload on Startup**: Call `astro_data.preload_all()` during app initialization
3. **Cache Aware**: Data is cached automatically, no need to cache again
4. **Memory Efficient**: Total memory footprint ~2-3 MB for all files
5. **Fast Access**: In-memory lookups after first load
