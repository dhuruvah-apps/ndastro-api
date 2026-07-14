# Muhurta (Electional Astrology)

Muhurta is the Vedic system of selecting auspicious time windows for important activities.
Two modules provide muhurta functionality:

- **`muhurta_advanced`** — low-level timing windows for a single day (Durmuhurta, Varjyam, Amrita Kala).
- **`muhurta_range`** — high-level date-range search that scores every candidate day across 70 life events using the classical five-formula system.

The public result dataclasses live in `ndastro_api.core.models.muhurta`.

---

## API Endpoints

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/api/v1/muhurta` | Single-day muhurta analysis (Durmuhurta, Varjyam, Amrita Kala) |
| `GET` | `/api/v1/muhurta/auspicious-range` | Find best dates in a range for a specific life event |

---

## `GET /api/v1/muhurta` — Single-Day Analysis

Returns timing windows for a single day at a given location.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float` | `12.971667` | Geographic latitude |
| `lon` | `float` | `77.593611` | Geographic longitude |
| `dateandtime` | `string` | now (UTC) | ISO 8601 datetime |
| `ayanamsa` | `string` | `lahiri` | Ayanamsa system |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `date` | `string` | Date in `YYYY-MM-DD` |
| `sunrise` / `sunset` | `string\|null` | Sunrise / sunset ISO datetimes |
| `tithi` | `int` | Lunar day (1–30) |
| `nakshatra` | `int` | Moon nakshatra (1–27) |
| `vara` | `int` | Vara / weekday (1=Sun … 7=Sat) |
| `durmuhurtas` | `DurmuhurtaResponse[]` | Inauspicious 48-min slots to avoid |
| `varjyam_windows` | `VarjyamResponse[]` | Nakshatra–tithi void periods |
| `amrita_kala` | `AmritaKalaResponse[]` | Very auspicious nectar windows |
| `kala_windows` | `AmritaKalaResponse[]` | Secondary auspicious windows |

---

## `GET /api/v1/muhurta/auspicious-range` — Date-Range Search

Scans a date range and returns the most auspicious days for a specific life event, ranked by a multi-factor Vedic score.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | `string` | ✓ | Start of search window — `YYYY-MM-DD` |
| `end_date` | `string` | ✓ | End (max 365 days from start) — `YYYY-MM-DD` |
| `event` | `EventType` | ✓ | Life event to find auspicious dates for (see [Event Types](#supported-event-types-eventtype)) |
| `lat` | `float` | — | Geographic latitude (default `12.971667`) |
| `lon` | `float` | — | Geographic longitude (default `77.593611`) |
| `ayanamsa` | `string` | — | Ayanamsa system (default `lahiri`) |
| `min_score` | `float` | — | Minimum score filter (0–16.5) |
| `limit` | `int` | — | Max results, 1–100 (default `30`) |
| `janma_nakshatra` | `int` | — | Birth nakshatra 1–27 → enables **Tara Bala** |
| `birth_rashi` | `int` | — | Birth Moon sign 1–12 → enables **Chandra Ashtama** |
| `travel_direction` | `string` | — | `north`/`south`/`east`/`west` → enables **Disha Shool** |
| `surgery_body_part` | `string` | — | Body part → enables **Moon body-part** caution |

`surgery_body_part` accepted values: `head`, `neck`, `arms`, `chest`, `heart`, `abdomen`, `kidneys`, `reproductive`, `thighs`, `knees`, `calves`, `feet`.

### Response Shape

```json
{
  "event": "marriage",
  "start_date": "2026-08-01",
  "end_date": "2026-12-31",
  "total_found": 30,
  "results": [ { ...AuspiciousDateResponse... } ]
}
```

### `AuspiciousDateResponse` Fields

#### Panchanga & Score

| Field | Type | Description |
|-------|------|-------------|
| `date` | `string` | `YYYY-MM-DD` |
| `event` | `string` | Event type value |
| `score` | `float` | Auspiciousness score (0–16.5, higher = better) |
| `tithi_number` / `tithi_name` | `int` / `string` | Lunar day and name |
| `paksha` | `string` | `shukla` (waxing) or `krishna` (waning) |
| `vara_number` / `vara_name` | `int` / `string` | Vara 1–7 and weekday name |
| `nakshatra` | `int` | Moon nakshatra 1–27 |
| `moon_rashi` | `int` | Moon sign 1–12 (Aries=1 … Pisces=12) |
| `yoga_name` / `yoga_number` | `string` / `int` | Nitya yoga |
| `muhurta_rating` | `float\|null` | JSON-sourced panchanga rating |
| `tithi_support` | `bool` | Tithi supports this event per panchanga data |
| `vara_support` | `bool` | Vara supports this event per panchanga data |
| `karana_support` | `bool` | Karana supports this event |
| `yoga_support` | `bool` | Yoga supports this event |
| `inauspicious_flags` | `string[]` | Which panchanga elements are inauspicious |
| `supporting_reasons` | `string[]` | Human-readable positive factors |
| `caution_reasons` | `string[]` | Human-readable warning factors |

#### Combustion Flags (Formula 2 events only)

| Field | Type | Description |
|-------|------|-------------|
| `jupiter_combust` | `bool` | Jupiter is within 11° of Sun (Asta) |
| `venus_combust` | `bool` | Venus is within 8° of Sun (Asta) |

#### Optional Personal Checks

| Field | Type | Requires | Description |
|-------|------|----------|-------------|
| `tara_bala` | `TaraResult\|null` | `janma_nakshatra` | 9-star strength from birth nakshatra |
| `chandra_ashtama` | `bool\|null` | `birth_rashi` | Moon in 6th/8th/12th from birth Rashi |
| `chandra_ashtama_house` | `int\|null` | `birth_rashi` | Which house Moon occupies (1–12) |
| `disha_shool_direction` | `string\|null` | travel events | Inauspicious travel direction for that weekday |
| `disha_shool_conflict` | `bool\|null` | `travel_direction` | `true` if supplied direction matches Disha Shool |
| `moon_body_part` | `string\|null` | `surgery_body_part` | Set when Moon transits the matching body-part sign |

#### Timing Windows

| Field | Type | Description |
|-------|------|-------------|
| `sunrise` / `sunset` | `string\|null` | Sunrise / sunset |
| `abhijit_muhurta` | `TimeWindowSummary\|null` | Midday auspicious window |
| `rahu_kalam` | `TimeWindowSummary\|null` | Rahu Kalam — **avoid** |
| `yamagandam` | `TimeWindowSummary\|null` | Yamagandam — **avoid** |
| `gulika` | `TimeWindowSummary\|null` | Gulika Kaal — **avoid** |
| `amrita_kala` | `TimeWindowSummary[]` | Amrit Kaal windows — **prefer** |
| `favorable_horas` | `HoraWindow[]` | Planetary hora slots matching the event |
| `lagna_windows` | `LagnaWindow[]` | Ascendant windows — **single-day queries only** |

---

## Scoring Algorithm

Each day is scored out of a theoretical maximum of **16.5**:

```
score = base_muhurta_rating          (0–10, from panchanga JSON data)
      + tithi_score                  (+2 good tithi / −2 bad tithi / 0 neutral)
      + vara_score                   (+2 good vara  / −2 bad vara  / 0 neutral)
      + nakshatra_score              (+2 if nakshatra in good set, else 0)
      + paksha_bonus                 (+0.5 for Shukla Paksha / waxing Moon)
      + combust_penalty              (−1 per combust benefic, Formula 2 events only)
```

Score is floored at `0.0`. Results are sorted highest-first before the `limit` is applied.

---

## The Five Vedic Formulas

Every event is assigned to exactly one formula that determines its preferred vara, nakshatra category, and lagna (ascendant) type.

### Formula 1 — Fixed & Structural

**Applies to:** Real Estate items 1–11 & 17, House Warming, House Shifting.

| Factor | Rule |
|--------|------|
| **Vara** | Monday, Wednesday, Thursday, Friday |
| **Avoid** | Tuesday (Mars aggression), Saturday (Saturn delays) |
| **Nakshatra** | Fixed / Dhruva — Rohini (4), U. Phalguni (12), U. Ashadha (21), U. Bhadrapada (26) |
| **Lagna** | Fixed signs (Taurus, Leo, Scorpio, Aquarius) |
| **Tithi avoid** | Rikta 4, 9, 14 + Amavasya 30 |

### Formula 2 — Soft & Devotional

**Applies to:** Finishing construction (plastering, flooring, painting), Samskaras (conception → ear-piercing), Marriage, Gold/jewellery/idol shopping, Spiritual vows.

| Factor | Rule |
|--------|------|
| **Vara** | Thursday (Jupiter) and Friday (Venus) **only** |
| **Nakshatra** | Mridu / Soft — Mrigashira (5), Chitra (14), Anuradha (17), Revati (27) |
| **Lagna** | Benefic ascendants ruled by Jupiter, Venus, or Mercury |
| **Extra check** | Jupiter and Venus must **not** be combust (within 11° / 8° of Sun) |
| **Moon** | Waxing / Shukla Paksha strongly preferred |

### Formula 3 — Fast & Commercial

**Applies to:** Sacred thread, Education, Age milestones (60th/70th/80th birthday), Job joining, Business start, Bank account, Digital launch, Vehicle & appliance purchase, Divorce filing.

| Factor | Rule |
|--------|------|
| **Vara** | Wednesday (Mercury), Sunday (Sun) |
| **Nakshatra** | Kshipra / Swift — Ashwini (1), Pushya (8), Hasta (13) |
| **Lagna** | Dual / Mutable signs (Gemini, Virgo, Sagittarius, Pisces) |
| **Tithis** | 2, 3, 5, 7, 10, **11** (Ekadashi), 13 |
| **Hora priority** | Mercury Hora (deals) and Jupiter Hora (wealth) |

### Formula 4 — Sharp & Dynamic

**Applies to:** Stock investments, Contracts, Debts, Loans, Lawsuits, International travel, Surgery, Medical treatment, Post-illness grooming, Ayurvedic treatment.

| Factor | Rule |
|--------|------|
| **Vara (surgery / legal)** | Tuesday (Mars) |
| **Vara (deep healing)** | Saturday (Saturn) |
| **Nakshatra** | Tikshna / Sharp — Ardra (6), Ashlesha (9), Jyeshtha (18), Mula (19) |
| **Lagna** | Movable signs (Aries, Cancer, Libra, Capricorn) |
| **Travel rule** | Check Disha Shool — avoid the direction marked below |
| **Surgery rule** | Never operate on the body part ruled by Moon's current transit sign |

**Disha Shool — inauspicious direction by weekday:**

| Weekday | Avoid |
|---------|-------|
| Monday | East |
| Tuesday | North |
| Wednesday | North |
| Thursday | East |
| Friday | South |
| Saturday | East |
| Sunday | West |

### Formula 5 — Growth & Fertile

**Applies to:** Agriculture & Farming (land tilling, sowing, irrigation, harvest, grain storage).

| Factor | Rule |
|--------|------|
| **Vara** | Monday, Wednesday, Thursday, Friday |
| **Nakshatra** | Chara / Movable — Punarvasu (7), Swati (15), Shravana (22), Dhanishta (23), Shatabhisha (24) |
| **Lagna** | Watery/Earth signs (Cancer, Scorpio, Pisces, Taurus) |
| **Moon** | Strong Moon in fertile constellations; waxing tithis preferred |

---

## Universal Four-Step Filter

Regardless of formula, every final date must pass:

1. **Subtract Rahu Kalam** — avoid the ~1.5-hour daily Rahu period (returned in `rahu_kalam`).
2. **Subtract Yamagandam & Gulika** — avoid both additional inauspicious daily windows.
3. **Tara Bala** (`janma_nakshatra` required) — Taras 3 (Vipat), 5 (Pratyak), 7 (Naidhana) are inauspicious; reject them.
4. **Chandra Bala** (`birth_rashi` required) — Moon in the 6th, 8th, or 12th house from your natal Moon sign is Chandra Ashtama; reject it.

---

## Supported Event Types (`EventType`)

### Category 1 — Real Estate & Construction

| Value | Formula | Event |
|-------|---------|-------|
| `land_purchase` | F1 | Buying land / plots (Bhoomi Kareed) |
| `groundbreaking` | F1 | Bhoomi Pujan / groundbreaking ceremony |
| `well_digging` | F1 | Digging a well, borewell, or water tank |
| `foundation_digging` | F1 | House foundation trench |
| `foundation_stone` | F1 | Laying the first foundation stone (Shilanyas) |
| `pillar_installation` | F1 | Basement pillar / pillar casting |
| `column_casting` | F1 | Main pillar / column casting |
| `brickwork` | F1 | Brickwork / wall construction (Chunai) |
| `door_frame_installation` | F1 | Main door frame installation (Chaukhat) |
| `roof_casting` | F1 | Roof concrete / roof casting (Lantor) |
| `staircase_construction` | F1 | Staircase construction |
| `boundary_wall` | F1 | Gates, fences, or boundary walls |
| `property_purchase` | F1 | Buying built property |
| `construction` | F1 | General construction (legacy) |
| `plastering` | F2 | Plastering work |
| `window_installation` | F2 | Installing windows and ventilation frames |
| `flooring_installation` | F2 | Flooring installation |
| `renovation` | F2 | Property renovations, extensions, or demolitions |
| `painting` | F2 | Painting the outer facade / final coating |

### Category 2 — Child & Youth Milestones (Samskaras)

| Value | Formula | Event |
|-------|---------|-------|
| `conception` | F2 | Garbhadhana |
| `baby_shower` | F2 | Valaikaappu / Godh Bharai |
| `childbirth_ritual` | F2 | Jatakarma |
| `naming_ceremony` | F2 | Namakaran / Naamakarandham |
| `cradle_ceremony` | F2 | Thottil Pujan |
| `first_solid_food` | F2 | Annaprashan / Choroonu |
| `first_haircut` | F2 | Mundan / Thala mudiathal |
| `ear_piercing` | F2 | Karnavedha / Kaadhukuthu |
| `sacred_thread` | F3 | Upanayana / Poonal |
| `education` | F3 | Vidyarambha / Akshara Abyasam |
| `puberty_ceremony` | F3 | Ritu Kala Samskaram / Manjal Neerattu Vizha |

### Category 3 — Marriage & Age Milestones

| Value | Formula | Event |
|-------|---------|-------|
| `marriage` | F2 | Vivah / Thirumanam |
| `shashti_poorthi` | F3 | 60th birthday milestone |
| `bhimaratha_shanthi` | F3 | 70th birthday / 1000 full moons |
| `sadhabishekam` | F3 | 80th birthday milestone |

### Category 4 — Business, Finance & Career

| Value | Formula | Event |
|-------|---------|-------|
| `job_joining` | F3 | Joining a job / taking oath |
| `business_start` | F3 | Business launch (Vyapar Arambha) |
| `bank_account_opening` | F3 | Opening a bank account |
| `stock_investment` | F4 | Stock market investments |
| `contract_signing` | F4 | Signing contracts / deeds / leases |
| `debt_payment` | F4 | Paying off debts |
| `loan_application` | F4 | Applying for loans or financial aid |
| `digital_launch` | F3 | Launching a website, app, or software |
| `merger_announcement` | F3 | Merger, acquisition, or partnership |
| `insurance_purchase` | F3 | Buying commercial insurance |

### Category 5 — Home, Shifting & Domestic

| Value | Formula | Event |
|-------|---------|-------|
| `house_warming` | F1 | Griha Pravesh / Pudhu Manai Puguzha |
| `house_shifting` | F1 | Shifting into a rented house |
| `vehicle_purchase` | F3 | Vahan Kareed / Vahana Pooja |
| `pet_adoption` | F3 | Adopting a pet or bringing livestock home |
| `appliance_purchase` | F3 | Buying heavy home appliances |
| `kitchen_ceremony` | F3 | First meal in a new kitchen (Chulha Pujan) |

### Category 6 — Health, Travel & Legal

| Value | Formula | Event |
|-------|---------|-------|
| `lawsuit_filing` | F4 | Filing lawsuits / initiating legal cases |
| `travel` | F4 | Long-distance journeys or pilgrimages (Yatra) |
| `international_travel` | F4 | Moving abroad / visa interviews |
| `surgery` | F4 | Elective medical surgeries |
| `medical_treatment` | F4 | Starting long-term medical treatment or therapy |
| `divorce_filing` | F4 | Filing for divorce or legal separation |
| `post_illness_grooming` | F4 | First shave or haircut after major illness |
| `ayurvedic_treatment` | F4 | Starting a special Ayurvedic medicine |

### Category 7 — Spiritual, Rituals & Shopping

| Value | Formula | Event |
|-------|---------|-------|
| `gold_purchase` | F2 | Buying gold, silver, or fine jewellery |
| `new_clothes` | F2 | Wearing new clothes or ornaments for the first time |
| `idol_installation` | F2 | Prana Pratishtha / Kumbhabhishekham |
| `spiritual_initiation` | F2 | Guru diksha / spiritual initiation |
| `vrata_diksha` | F2 | Starting a fast, vow, or long-term practice |
| `creative_project` | F2 | Starting a creative project or writing a book |
| `ancestral_ritual` | *(inverted)* | Tarpanam / Shradh — Amavasya is the best day |

!!! note "Ancestral Ritual — Inverted Rules"
    `ancestral_ritual` uses inverted timing: Amavasya (tithi 30) is preferred, and Saturday/Sunday are favored. The score reflects this inversion.

### Category 8 — Agriculture & Farming

| Value | Formula | Event |
|-------|---------|-------|
| `land_tilling` | F5 | Tilling or preparing agricultural land |
| `crop_sowing` | F5 | Planting crops / sowing seeds |
| `irrigation_installation` | F5 | Installing irrigation systems or farm boring |
| `crop_harvesting` | F5 | Harvesting crops (Pongal / Makar Sankranti) |
| `grain_storage` | F5 | First grain storage in the granary |

---

## Result Models (`ndastro_api.core.models.muhurta`)

### `TimeWindowSummary`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Window label (e.g. `rahu_kalam`, `amrita`, `abhijit_muhurta`) |
| `start` | `str` | ISO 8601 start datetime |
| `end` | `str` | ISO 8601 end datetime |
| `duration_minutes` | `float` | Duration in minutes |

### `HoraWindow`

Returned in `favorable_horas` — only the hora slots that match the requested event type are included.

| Field | Type | Description |
|-------|------|-------------|
| `hora_number` | `int` | Hora slot 1–24 (from sunrise) |
| `lord_code` | `str` | Planet code: `SU`, `MO`, `MA`, `ME`, `JU`, `VE`, `SA` |
| `lord_name` | `str` | Planet name |
| `start` / `end` | `str` | ISO start / end |
| `duration_minutes` | `float` | Always `60.0` |

### `LagnaWindow`

Populated **only for single-day queries** (`start_date == end_date`). The ascendant is sampled every 20 minutes and consecutive same-sign intervals are merged.

| Field | Type | Description |
|-------|------|-------------|
| `sign_number` | `int` | Rashi 1–12 |
| `sign_name` | `str` | Sign name (e.g. `Leo`) |
| `is_favorable` | `bool` | Whether the sign is in the favorable set for the event formula |
| `start` / `end` | `str` | ISO start / end of this ascendant window |
| `duration_minutes` | `float` | Duration (~100–120 min per sign) |

### `TaraResult`

Returned when `janma_nakshatra` is supplied.

| Field | Type | Description |
|-------|------|-------------|
| `tara_number` | `int` | Tara 1–9 |
| `tara_name` | `str` | `Janma`, `Sampat`, `Vipat`, `Kshema`, `Pratyak`, `Sadhana`, `Naidhana`, `Mitra`, `Param Mitra` |
| `is_auspicious` | `bool` | `false` for Taras 3, 5, 7 |
| `description` | `str` | One-line classical description |

**Calculation:** `count = ((current_nakshatra − janma_nakshatra) % 27) + 1`, then `tara = ((count − 1) % 9) + 1`.

---

## Usage Examples

### Best Marriage Dates This Year

```
GET /api/v1/muhurta/auspicious-range
  ?start_date=2026-08-01
  &end_date=2026-12-31
  &event=marriage
  &lat=12.971667
  &lon=77.593611
  &janma_nakshatra=7
  &birth_rashi=4
  &limit=10
```

Returns the 10 highest-scoring marriage dates. Each result shows Tara Bala, Chandra Ashtama, favorable hora slots, and all inauspicious windows to avoid.

### Single-Day Deep Analysis with Lagna

```
GET /api/v1/muhurta/auspicious-range
  ?start_date=2026-09-15
  &end_date=2026-09-15
  &event=house_warming
```

Because `start_date == end_date`, the response additionally includes `lagna_windows` — every ~2-hour ascendant cycle labelled favorable or unfavorable for house warming (Formula 1: Fixed sign lagna required).

### Surgery Timing with Moon Check

```
GET /api/v1/muhurta/auspicious-range
  ?start_date=2026-08-01
  &end_date=2026-08-31
  &event=surgery
  &surgery_body_part=heart
```

Days where the Moon transits Leo (rules the heart) carry `moon_body_part = "heart"` and a warning in `caution_reasons`.

### Safe Travel Direction

```
GET /api/v1/muhurta/auspicious-range
  ?start_date=2026-08-01
  &end_date=2026-08-31
  &event=travel
  &travel_direction=north
```

Each result shows `disha_shool_direction` (the unsafe direction that day) and `disha_shool_conflict = true/false` for the supplied direction.

---

## Low-Level Service Reference (`muhurta_advanced`)

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `MINUTES_PER_MUHURTA` | 48 | Each muhurta is 48 minutes (1/30th of a day) |
| Total per day | 30 | A full day = 30 muhurtas |

### `MuhurtaQuality` Enum

| Value | Meaning |
|-------|---------|
| `EXCELLENT` | Best for all activities |
| `GOOD` | Suitable for most |
| `AVERAGE` | Neutral — proceed with care |
| `POOR` | Avoid if possible |
| `INAUSPICIOUS` | Strongly avoid |

### `get_durmuhurtas(sunrise) → list[DurmuhurtaWindow]`

Returns four Durmuhurta windows (muhurta indices 6, 14, 23, 28 from sunrise). Each is 48 minutes.

### `get_varjyam_windows(tithi, nakshatra, tithi_end_time) → list[VarjyamWindow]`

Returns Varjyam void windows based on 12 classical nakshatra–tithi pairs.

### `get_amrita_kala_windows(weekday, nakshatra, sunrise, sunset) → (amrita_windows, kala_windows)`

Returns Amrita Kala (very auspicious) and Kala windows based on weekday–nakshatra combinations.

!!! note "Abhijit Muhurta — Wednesday Exception"
    `get_abhijit_muhurta` (from the panchanga module) returns the midday auspicious window.
    It returns `None` on Wednesdays when `exclude_wednesday=True` (classical rule).
| `MINUTES_PER_MUHURTA` | 48 | Each muhurta is 48 minutes long (1/30th of a day) |
| Total muhurtas per day | 30 | A full day (24h) has 30 muhurtas |

---

## `MuhurtaQuality` Enum

| Value | Meaning |
|-------|---------|
| `EXCELLENT` | Best for all activities |
| `GOOD` | Suitable for most activities |
| `AVERAGE` | Neutral, proceed with care |
| `POOR` | Avoid if possible |
| `INAUSPICIOUS` | Strongly avoid |

---

## Functions

### `get_durmuhurtas`

```python
get_durmuhurtas(sunrise: datetime) -> list[DurmuhurtaWindow]
```

Returns the Durmuhurta windows for the day — inauspicious 48-minute periods that should be avoided for starting new activities.

**Algorithm:** Durmuhurtas occur at muhurta indices `[6, 14, 23, 28]` from sunrise. Each window starts at `sunrise + (index × 48 minutes)` and lasts 48 minutes.

**Returns:** List of `DurmuhurtaWindow`:

| Field | Type | Description |
|-------|------|-------------|
| `start` | `datetime` | Window start time |
| `end` | `datetime` | Window end time |
| `name` | `str` | Name of the Durmuhurta |
| `weekday_name` | `str` | Weekday this applies to |
| `quality` | `MuhurtaQuality` | Always `INAUSPICIOUS` |

---

### `get_varjyam_windows`

```python
get_varjyam_windows(
    tithi: int,
    nakshatra: int,
    tithi_end_time: datetime
) -> list[VarjyamWindow]
```

Returns Varjyam (inauspicious) windows based on the nakshatra–tithi combination. Varjyam periods are derived from 12 classical nakshatra pairs that produce harmful combinations on specific tithis.

**Returns:** List of `VarjyamWindow`:

| Field | Type | Description |
|-------|------|-------------|
| `start` | `datetime` | Window start time |
| `end` | `datetime` | Window end time |
| `nakshatra` | `int` | Triggering nakshatra |
| `tithi` | `int` | Triggering tithi |
| `quality` | `MuhurtaQuality` | Always `INAUSPICIOUS` |

---

### `get_amrita_kala_windows`

```python
get_amrita_kala_windows(
    weekday: int,
    nakshatra: int,
    sunrise: datetime,
    sunset: datetime
) -> tuple[list[AmritaKalaWindow], list[KalaWindow]]
```

Returns both Amrita Kala (nectar period — very auspicious) and Kala (specific planetary period) windows.

**Returns:** `(amrita_windows, kala_windows)` — two separate lists.

**`AmritaKalaWindow`:**

| Field | Type | Description |
|-------|------|-------------|
| `start` | `datetime` | Window start |
| `end` | `datetime` | Window end |
| `quality` | `MuhurtaQuality` | `EXCELLENT` |
| `ruling_planet` | `str` | Planet governing this window |

**`KalaWindow`:**

| Field | Type | Description |
|-------|------|-------------|
| `start` | `datetime` | Window start |
| `end` | `datetime` | Window end |
| `quality` | `MuhurtaQuality` | `GOOD` or `EXCELLENT` |
| `name` | `str` | Kala name |

---

## Typical Muhurta Workflow

For a given day, the sequence of analysis is:

1. Calculate `sunrise` and `sunset` using the sunrise-sunset API endpoint.
2. Get Panchanga data (`tithi`, `nakshatra`, `vara`) for the day.
3. Call `get_durmuhurtas(sunrise)` → avoid these windows.
4. Call `get_varjyam_windows(tithi, nakshatra, tithi_end_time)` → avoid these windows.
5. Call `get_amrita_kala_windows(weekday, nakshatra, sunrise, sunset)` → prefer these windows.
6. Schedule the activity in an Amrita Kala or Kala window that does not overlap with Durmuhurta or Varjyam.

---

## Integration with Abhijit Muhurta

The `panchanga` module's `get_abhijit_muhurta` (see [Nakshatra & Panchanga](nakshatra_panchanga.md)) provides the midday auspicious window. Abhijit combined with Amrita Kala produces the most powerful timing.

!!! note "Wednesday Exception"
    Abhijit Muhurta is traditionally not used on Wednesdays as it is considered inauspicious for that weekday.
