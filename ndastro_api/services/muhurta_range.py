"""Muhurta auspicious date-range search service.

Scans a date range and scores each day for a specified life event using
classical Vedic electional astrology (muhurta shastra) rules: tithi, vara,
nakshatra, yoga, and lunar paksha.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, replace as dc_replace
from datetime import UTC, date, datetime, timedelta
from enum import Enum
from functools import lru_cache
from typing import Any

from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.core import get_ascendent_position, get_planet_position, get_sunrise_sunset
from ndastro_engine.enums import Planets
from ndastro_engine.utils import normalize_degree

from ndastro_api.core.models.muhurta import (
    AuspiciousDateResult,
    HoraWindow,
    LagnaWindow,
    TaraResult,
    TimeWindowSummary,
)
from ndastro_api.services.muhurta_advanced import AmritaKalaWindow, get_amrita_kala_windows
from ndastro_api.services.panchanga import (
    PanchangaDataResult,
    PanchangaActivitySupport,
    get_abhijit_muhurta,
    get_activity_support,
    get_gulika,
    get_panchanga_with_data,
    get_rahu_kalam,
    get_yamagandam,
)
from ndastro_api.services.position import get_nakshatra_and_pada

MAX_DATE_RANGE_DAYS = 365
MAX_RESULTS = 100

# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------

class EventType(str, Enum):
    """Supported muhurta event types — all 70 life events across 8 Vedic categories."""

    # ---- Category 1: Real Estate & Heavy Construction (Vastu) ----
    LAND_PURCHASE             = "land_purchase"          # Buying land / plots
    GROUNDBREAKING            = "groundbreaking"         # Bhoomi Pujan
    WELL_DIGGING              = "well_digging"           # Well / borewell / water tank
    FOUNDATION_DIGGING        = "foundation_digging"     # Foundation trench
    FOUNDATION_STONE          = "foundation_stone"       # Shilanyas
    PILLAR_INSTALLATION       = "pillar_installation"    # Basement pillar casting
    COLUMN_CASTING            = "column_casting"         # Main column / beam casting
    BRICKWORK                 = "brickwork"              # Chunai / wall construction
    DOOR_FRAME_INSTALLATION   = "door_frame_installation"  # Chaukhat / main door frame
    ROOF_CASTING              = "roof_casting"           # Lantor / roof concrete
    STAIRCASE_CONSTRUCTION    = "staircase_construction"
    PLASTERING                = "plastering"
    WINDOW_INSTALLATION       = "window_installation"
    FLOORING_INSTALLATION     = "flooring_installation"
    RENOVATION                = "renovation"             # Extensions / demolitions
    PAINTING                  = "painting"               # Outer facade / final coat
    BOUNDARY_WALL             = "boundary_wall"          # Gates, fences, compound wall
    PROPERTY_PURCHASE         = "property_purchase"      # Buying built property
    CONSTRUCTION              = "construction"           # General construction (legacy)

    # ---- Category 2: Child & Youth Milestones (Samskaras) ----
    CONCEPTION                = "conception"             # Garbhadhana
    BABY_SHOWER               = "baby_shower"            # Valaikaappu / Godh Bharai
    CHILDBIRTH_RITUAL         = "childbirth_ritual"      # Jatakarma
    NAMING_CEREMONY           = "naming_ceremony"        # Namakaran
    CRADLE_CEREMONY           = "cradle_ceremony"        # Thottil Pujan
    FIRST_SOLID_FOOD          = "first_solid_food"       # Annaprashan / Choroonu
    FIRST_HAIRCUT             = "first_haircut"          # Mundan / Thala mudiathal
    EAR_PIERCING              = "ear_piercing"           # Karnavedha / Kaadhukuthu
    SACRED_THREAD             = "sacred_thread"          # Upanayana / Poonal
    EDUCATION                 = "education"              # Vidyarambha / Akshara Abyasam
    PUBERTY_CEREMONY          = "puberty_ceremony"       # Ritu Kala Samskaram

    # ---- Category 3: Marriage & Age Milestones ----
    MARRIAGE                  = "marriage"               # Vivah / Thirumanam
    SHASHTI_POORTHI           = "shashti_poorthi"        # 60th birthday
    BHIMARATHA_SHANTHI        = "bhimaratha_shanthi"     # 70th birthday / 1000 full moons
    SADHABISHEKAM             = "sadhabishekam"          # 80th birthday milestone

    # ---- Category 4: Business, Finance & Career ----
    JOB_JOINING               = "job_joining"            # Joining / oath-taking
    BUSINESS_START            = "business_start"         # Vyapar Arambha
    BANK_ACCOUNT_OPENING      = "bank_account_opening"
    STOCK_INVESTMENT          = "stock_investment"       # Muhurat trading
    CONTRACT_SIGNING          = "contract_signing"       # Deeds / leases
    DEBT_PAYMENT              = "debt_payment"           # Paying off debts
    LOAN_APPLICATION          = "loan_application"       # Applying for loans
    DIGITAL_LAUNCH            = "digital_launch"         # Website / app / software
    MERGER_ANNOUNCEMENT       = "merger_announcement"    # M&A / partnership
    INSURANCE_PURCHASE        = "insurance_purchase"

    # ---- Category 5: Home, Shifting & Domestic Lifestyle ----
    HOUSE_WARMING             = "house_warming"          # Griha Pravesh
    HOUSE_SHIFTING            = "house_shifting"         # Moving into rented house
    VEHICLE_PURCHASE          = "vehicle_purchase"       # Vahana Pooja
    PET_ADOPTION              = "pet_adoption"           # Bringing animal / livestock home
    APPLIANCE_PURCHASE        = "appliance_purchase"     # Heavy home machinery
    KITCHEN_CEREMONY          = "kitchen_ceremony"       # Chulha Pujan / first meal

    # ---- Category 6: Health, Travel & Legal ----
    LAWSUIT_FILING            = "lawsuit_filing"         # Initiating legal cases
    TRAVEL                    = "travel"                 # Yatra / short journeys
    INTERNATIONAL_TRAVEL      = "international_travel"   # Moving abroad / visa
    SURGERY                   = "surgery"                # Elective medical procedures
    MEDICAL_TREATMENT         = "medical_treatment"      # Long-term treatment / therapy
    DIVORCE_FILING            = "divorce_filing"         # Legal separation
    POST_ILLNESS_GROOMING     = "post_illness_grooming"  # First shave / cut after illness
    AYURVEDIC_TREATMENT       = "ayurvedic_treatment"    # Special Ayurvedic medicine

    # ---- Category 7: Spiritual, Rituals & Shopping ----
    GOLD_PURCHASE             = "gold_purchase"          # Akshaya Tritiya / Dhanteras
    NEW_CLOTHES               = "new_clothes"            # First wearing of new clothes
    IDOL_INSTALLATION         = "idol_installation"      # Prana Pratishtha / Kumbhabhishekham
    SPIRITUAL_INITIATION      = "spiritual_initiation"   # Guru diksha
    VRATA_DIKSHA              = "vrata_diksha"           # Starting a fast / vow / Nonbu
    CREATIVE_PROJECT          = "creative_project"       # New creative work / writing
    ANCESTRAL_RITUAL          = "ancestral_ritual"       # Tarpanam / Shradh

    # ---- Category 8: Agriculture & Farming ----
    LAND_TILLING              = "land_tilling"           # Tilling / preparing land
    CROP_SOWING               = "crop_sowing"            # Planting / sowing seeds
    IRRIGATION_INSTALLATION   = "irrigation_installation"  # Irrigation system / farm boring
    CROP_HARVESTING           = "crop_harvesting"        # Pongal / Makar Sankranti harvesting
    GRAIN_STORAGE             = "grain_storage"          # First storage in granary


# ---------------------------------------------------------------------------
# Per-event Vedic criteria (good/bad tithis, varas, nakshatras)
# Vara numbers: Sun=1 Mon=2 Tue=3 Wed=4 Thu=5 Fri=6 Sat=7
# Nakshatra numbers: 1-27
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _EventCriteria:
    good_tithis: frozenset[int]
    bad_tithis: frozenset[int]
    good_varas: frozenset[int]
    bad_varas: frozenset[int]
    good_nakshatras: frozenset[int]
    activity_key: str  # string matched against JSON auspiciousFor lists


_GOOD_TITHIS_GENERAL: frozenset[int] = frozenset({2, 3, 5, 7, 10, 12, 13})
_BAD_TITHIS_GENERAL: frozenset[int] = frozenset({4, 9, 14, 30})
_F3_TITHIS:          frozenset[int] = frozenset({2, 3, 5, 7, 10, 11, 13})  # Formula 3 adds Ekadashi
_FIXED_NAKSHATRAS: frozenset[int] = frozenset({4, 12, 21, 26})   # Rohini, U.Phalguni, U.Ashadha, U.Bhadrapada
_SWIFT_NAKSHATRAS: frozenset[int] = frozenset({1, 8, 13})         # Ashwini, Pushya, Hasta
_SOFT_NAKSHATRAS:  frozenset[int] = frozenset({5, 14, 17, 27})   # Mrigashira, Chitra, Anuradha, Revati
_SHARP_NAKSHATRAS: frozenset[int] = frozenset({6, 9, 18, 19})    # Ardra, Ashlesha, Jyeshtha, Mula
# Formula 5: Chara (movable) + Shravana, Dhanishta, Shatabhisha
_AGRI_NAKSHATRAS:  frozenset[int] = frozenset({7, 15, 22, 23, 24})  # Punarvasu, Swati, Shravana, Dhanishta, Shatabhisha

# --------------- Vara groups per formula ---------------
# F1 & F5 (stable/benefic): Mon(2) Wed(4) Thu(5) Fri(6) — NO Tuesday
_F1_VARAS = frozenset({2, 4, 5, 6})
_F1_BAD   = frozenset({3, 7})
# F2 (soft/devotional): Thu(5) Fri(6) only
_F2_VARAS = frozenset({5, 6})
_F2_BAD   = frozenset({3, 7})
# F3 (fast/commercial): Wed(4) Sun(1)
_F3_VARAS = frozenset({4, 1})
_F3_BAD   = frozenset({7})
# F4 sub-groups
_F4_SURGERY_VARAS  = frozenset({3})         # Tue/Mars for cutting
_F4_HEALING_VARAS  = frozenset({7})         # Sat/Saturn for deep healing
_F4_FINANCE_VARAS  = frozenset({3, 7})      # both for sharp financial moves
_F4_BAD_SURGERY    = frozenset({2, 7})
_F4_BAD_HEALING    = frozenset({2})
_F4_BAD_FINANCE    = frozenset({5})

_EVENT_CRITERIA: dict[EventType, _EventCriteria] = {
    # ====================================================================
    # FORMULA 1: Fixed & Structural — Mon Wed Thu Fri, Fixed nakshatras
    # Applies: items 1-11, 17 (structural construction), 43-44 (house)
    # ====================================================================
    EventType.LAND_PURCHASE: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="land purchase"),
    EventType.GROUNDBREAKING: _EventCriteria(
        good_tithis=frozenset({2,3,5,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="groundbreaking"),
    EventType.WELL_DIGGING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=frozenset({4, 22, 27}), activity_key="well digging"),
    EventType.FOUNDATION_DIGGING: _EventCriteria(
        good_tithis=frozenset({2,3,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="foundation digging"),
    EventType.FOUNDATION_STONE: _EventCriteria(
        good_tithis=frozenset({2,3,5,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="foundation stone"),
    EventType.PILLAR_INSTALLATION: _EventCriteria(
        good_tithis=frozenset({2,3,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="pillar installation"),
    EventType.COLUMN_CASTING: _EventCriteria(
        good_tithis=frozenset({2,3,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="column casting"),
    EventType.BRICKWORK: _EventCriteria(
        good_tithis=frozenset({2,3,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="brickwork"),
    EventType.DOOR_FRAME_INSTALLATION: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="door frame"),
    EventType.ROOF_CASTING: _EventCriteria(
        good_tithis=frozenset({2,3,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="roof casting"),
    EventType.STAIRCASE_CONSTRUCTION: _EventCriteria(
        good_tithis=frozenset({2,3,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="staircase"),
    EventType.BOUNDARY_WALL: _EventCriteria(
        good_tithis=frozenset({2,3,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="boundary wall"),
    EventType.PROPERTY_PURCHASE: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="property purchase"),
    EventType.CONSTRUCTION: _EventCriteria(
        good_tithis=frozenset({2,3,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="construction"),
    EventType.HOUSE_WARMING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="house warming"),
    EventType.HOUSE_SHIFTING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="house shifting"),

    # ====================================================================
    # FORMULA 2: Soft & Devotional — Thu Fri, Mridu (Soft) nakshatras
    # Applies: items 12-16 (finishing work), 18-25 (Samskaras),
    #          29 (Marriage), 57-62 (Spiritual/Shopping)
    # ====================================================================
    # Finishing construction (items 12-16)
    EventType.PLASTERING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="plastering"),
    EventType.WINDOW_INSTALLATION: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="window installation"),
    EventType.FLOORING_INSTALLATION: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="flooring"),
    EventType.RENOVATION: _EventCriteria(
        good_tithis=frozenset({2,3,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="renovation"),
    EventType.PAINTING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="painting"),
    # Samskaras (items 18-25)
    EventType.CONCEPTION: _EventCriteria(
        good_tithis=frozenset({2,3,5,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="conception"),
    EventType.BABY_SHOWER: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="baby shower"),
    EventType.CHILDBIRTH_RITUAL: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="childbirth"),
    EventType.NAMING_CEREMONY: _EventCriteria(
        good_tithis=frozenset({2,3,5,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="naming ceremony"),
    EventType.CRADLE_CEREMONY: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="cradle ceremony"),
    EventType.FIRST_SOLID_FOOD: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="first solid food"),
    EventType.FIRST_HAIRCUT: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="first haircut"),
    EventType.EAR_PIERCING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="ear piercing"),
    # Marriage (item 29) — keep classical marriage nakshatras
    EventType.MARRIAGE: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=frozenset({4,6,8,9,11,14,30}),
        good_varas=_F2_VARAS, bad_varas=frozenset({1,3,7}),
        good_nakshatras=frozenset({4,8,12,17,21,22,26,27}), activity_key="marriage"),
    # Spiritual & Shopping (items 57-62)
    EventType.GOLD_PURCHASE: _EventCriteria(
        good_tithis=frozenset({3,2,5,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="gold purchase"),
    EventType.NEW_CLOTHES: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="new clothes"),
    EventType.IDOL_INSTALLATION: _EventCriteria(
        good_tithis=frozenset({2,3,5,7,10,12,13}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=frozenset({5,8,17,27}), activity_key="idol installation"),
    EventType.SPIRITUAL_INITIATION: _EventCriteria(
        good_tithis=frozenset({2,3,5,10,11}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=frozenset({5,8,17,27}), activity_key="spiritual"),
    EventType.VRATA_DIKSHA: _EventCriteria(
        good_tithis=frozenset({2,3,5,7,10,11}), bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="vrata"),
    EventType.CREATIVE_PROJECT: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F2_VARAS, bad_varas=_F2_BAD,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="creative project"),
    EventType.ANCESTRAL_RITUAL: _EventCriteria(  # inverted — Amavasya is best
        good_tithis=frozenset({30,15,9,4,14}), bad_tithis=frozenset({2,3}),
        good_varas=frozenset({7,1}), bad_varas=frozenset({6}),
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="ancestral ritual"),

    # ====================================================================
    # FORMULA 3: Fast & Commercial — Wed(4) Sun(1), Swift nakshatras
    # Tithis: {2,3,5,7,10,11,13} (includes Ekadashi)
    # Applies: items 26-28, 30-35, 40-42, 45-48, 54
    # ====================================================================
    EventType.SACRED_THREAD: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="sacred thread"),
    EventType.EDUCATION: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="education"),
    EventType.PUBERTY_CEREMONY: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="puberty ceremony"),
    EventType.SHASHTI_POORTHI: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="shashti poorthi"),
    EventType.BHIMARATHA_SHANTHI: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="bhimaratha shanthi"),
    EventType.SADHABISHEKAM: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="sadhabishekam"),
    EventType.JOB_JOINING: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="job joining"),
    EventType.BUSINESS_START: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="business"),
    EventType.BANK_ACCOUNT_OPENING: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="bank account"),
    EventType.DIGITAL_LAUNCH: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="digital launch"),
    EventType.MERGER_ANNOUNCEMENT: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="merger"),
    EventType.INSURANCE_PURCHASE: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="insurance"),
    EventType.VEHICLE_PURCHASE: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="vehicle purchase"),
    EventType.PET_ADOPTION: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="pet adoption"),
    EventType.APPLIANCE_PURCHASE: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="appliance purchase"),
    EventType.KITCHEN_CEREMONY: _EventCriteria(
        good_tithis=_F3_TITHIS, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F3_VARAS, bad_varas=_F3_BAD,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="kitchen ceremony"),
    EventType.DIVORCE_FILING: _EventCriteria(  # inverted — avoid auspicious days
        good_tithis=frozenset({4,9,14}), bad_tithis=frozenset({2,3,12}),
        good_varas=_F3_VARAS, bad_varas=frozenset({5}),
        good_nakshatras=_SHARP_NAKSHATRAS, activity_key="divorce"),

    # ====================================================================
    # FORMULA 4: Sharp & Dynamic — Tue for surgery/legal, Sat for healing
    # Applies: items 36-39 (sharp finance), 49-53, 55-56 (health/legal/travel)
    # ====================================================================
    EventType.STOCK_INVESTMENT: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F4_FINANCE_VARAS, bad_varas=_F4_BAD_FINANCE,
        good_nakshatras=_SHARP_NAKSHATRAS, activity_key="investment"),
    EventType.CONTRACT_SIGNING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F4_FINANCE_VARAS, bad_varas=_F4_BAD_FINANCE,
        good_nakshatras=_SHARP_NAKSHATRAS, activity_key="contract"),
    EventType.DEBT_PAYMENT: _EventCriteria(
        good_tithis=frozenset({4,9,14,2,10,13}), bad_tithis=frozenset({15}),
        good_varas=_F4_FINANCE_VARAS, bad_varas=_F4_BAD_FINANCE,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="debt payment"),
    EventType.LOAN_APPLICATION: _EventCriteria(
        good_tithis=frozenset({4,9,14}), bad_tithis=frozenset({2,3,15}),
        good_varas=_F4_FINANCE_VARAS, bad_varas=_F4_BAD_FINANCE,
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="loan"),
    EventType.LAWSUIT_FILING: _EventCriteria(
        good_tithis=frozenset({6,3,7,10,13}), bad_tithis=frozenset({4,9,14}),
        good_varas=_F4_SURGERY_VARAS, bad_varas=frozenset({2,5}),
        good_nakshatras=_SHARP_NAKSHATRAS, activity_key="lawsuit"),
    EventType.TRAVEL: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=frozenset({4,5,6}), bad_varas=frozenset({7}),
        good_nakshatras=_SWIFT_NAKSHATRAS, activity_key="travel"),
    EventType.INTERNATIONAL_TRAVEL: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F4_SURGERY_VARAS, bad_varas=frozenset({2,7}),
        good_nakshatras=frozenset({1,7,8,13,22}), activity_key="travel"),
    EventType.SURGERY: _EventCriteria(
        good_tithis=frozenset({2,3,5,6,7,10,12,13}), bad_tithis=frozenset({4,9,14,15,30}),
        good_varas=_F4_SURGERY_VARAS, bad_varas=_F4_BAD_SURGERY,
        good_nakshatras=_SHARP_NAKSHATRAS, activity_key="surgery"),
    EventType.MEDICAL_TREATMENT: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F4_HEALING_VARAS, bad_varas=_F4_BAD_HEALING,
        good_nakshatras=frozenset({1,8,17}), activity_key="medical treatment"),
    EventType.POST_ILLNESS_GROOMING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F4_HEALING_VARAS, bad_varas=_F4_BAD_HEALING,
        good_nakshatras=_SOFT_NAKSHATRAS, activity_key="grooming"),
    EventType.AYURVEDIC_TREATMENT: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F4_HEALING_VARAS, bad_varas=_F4_BAD_HEALING,
        good_nakshatras=frozenset({1,8,17}), activity_key="ayurvedic"),

    # ====================================================================
    # FORMULA 5: Growth & Fertile — Mon Wed Thu Fri, Chara (movable) nakshatras
    # Applies: items 63-67 (Agriculture)
    # ====================================================================
    EventType.LAND_TILLING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_AGRI_NAKSHATRAS, activity_key="land tilling"),
    EventType.CROP_SOWING: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_AGRI_NAKSHATRAS, activity_key="crop sowing"),
    EventType.IRRIGATION_INSTALLATION: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=frozenset({7,15,22,23,24}), activity_key="irrigation"),
    EventType.CROP_HARVESTING: _EventCriteria(
        good_tithis=frozenset({2,3,5,7,10,12,13,15}), bad_tithis=frozenset({4,9,14,30}),
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_AGRI_NAKSHATRAS, activity_key="harvesting"),
    EventType.GRAIN_STORAGE: _EventCriteria(
        good_tithis=_GOOD_TITHIS_GENERAL, bad_tithis=_BAD_TITHIS_GENERAL,
        good_varas=_F1_VARAS, bad_varas=_F1_BAD,
        good_nakshatras=_FIXED_NAKSHATRAS, activity_key="grain storage"),
}


# ---------------------------------------------------------------------------
# Planetary hora constants (Chaldean order)
# ---------------------------------------------------------------------------

_CHALDEAN_ORDER: tuple[str, ...] = ("SA", "JU", "MA", "SU", "VE", "ME", "MO")
_CHALDEAN_NAMES: dict[str, str] = {
    "SA": "Saturn", "JU": "Jupiter", "MA": "Mars", "SU": "Sun",
    "VE": "Venus",  "ME": "Mercury", "MO": "Moon",
}
# Python weekday Mon=0..Sun=6 → Chaldean start index for 1st hora of that day
_DAY_HORA_START_IDX: dict[int, int] = {
    0: 6,  # Monday    → Moon
    1: 2,  # Tuesday   → Mars
    2: 5,  # Wednesday → Mercury
    3: 1,  # Thursday  → Jupiter
    4: 4,  # Friday    → Venus
    5: 0,  # Saturday  → Saturn
    6: 3,  # Sunday    → Sun
}
_EVENT_FAVORABLE_HORA_LORDS: dict[EventType, frozenset[str]] = {
    # Category 1: Real Estate & Construction
    EventType.LAND_PURCHASE:           frozenset({"MA", "JU"}),
    EventType.GROUNDBREAKING:          frozenset({"MA", "JU"}),
    EventType.WELL_DIGGING:            frozenset({"MO", "JU"}),
    EventType.FOUNDATION_DIGGING:      frozenset({"MA", "SA"}),
    EventType.FOUNDATION_STONE:        frozenset({"MA", "JU"}),
    EventType.PILLAR_INSTALLATION:     frozenset({"MA", "SA", "JU"}),
    EventType.COLUMN_CASTING:          frozenset({"MA", "SA"}),
    EventType.BRICKWORK:               frozenset({"MA", "SA"}),
    EventType.DOOR_FRAME_INSTALLATION: frozenset({"MO", "JU", "VE"}),
    EventType.ROOF_CASTING:            frozenset({"MA", "SA"}),
    EventType.STAIRCASE_CONSTRUCTION:  frozenset({"MA", "SA"}),
    EventType.PLASTERING:              frozenset({"ME", "VE"}),
    EventType.WINDOW_INSTALLATION:     frozenset({"ME", "VE"}),
    EventType.FLOORING_INSTALLATION:   frozenset({"MO", "VE"}),
    EventType.RENOVATION:              frozenset({"MA", "SA"}),
    EventType.PAINTING:                frozenset({"VE", "ME"}),
    EventType.BOUNDARY_WALL:           frozenset({"MA", "SA"}),
    EventType.PROPERTY_PURCHASE:       frozenset({"MA", "JU"}),
    EventType.CONSTRUCTION:            frozenset({"MA", "SA"}),
    # Category 2: Child & Youth
    EventType.CONCEPTION:              frozenset({"JU", "MO", "VE"}),
    EventType.BABY_SHOWER:             frozenset({"JU", "MO", "VE"}),
    EventType.CHILDBIRTH_RITUAL:       frozenset({"JU", "MO"}),
    EventType.NAMING_CEREMONY:         frozenset({"JU", "ME"}),
    EventType.CRADLE_CEREMONY:         frozenset({"JU", "MO"}),
    EventType.FIRST_SOLID_FOOD:        frozenset({"JU", "MO"}),
    EventType.FIRST_HAIRCUT:           frozenset({"JU", "ME"}),
    EventType.EAR_PIERCING:            frozenset({"ME", "VE"}),
    EventType.SACRED_THREAD:           frozenset({"JU", "ME"}),
    EventType.EDUCATION:               frozenset({"JU", "ME"}),
    EventType.PUBERTY_CEREMONY:        frozenset({"JU", "MO", "VE"}),
    # Category 3: Marriage & Age Milestones
    EventType.MARRIAGE:                frozenset({"JU", "VE", "ME"}),
    EventType.SHASHTI_POORTHI:         frozenset({"JU", "SU", "ME"}),
    EventType.BHIMARATHA_SHANTHI:      frozenset({"JU", "SU", "ME"}),
    EventType.SADHABISHEKAM:           frozenset({"JU", "SU", "ME"}),
    # Category 4: Business, Finance & Career
    EventType.JOB_JOINING:             frozenset({"SU", "JU"}),
    EventType.BUSINESS_START:          frozenset({"ME", "JU"}),
    EventType.BANK_ACCOUNT_OPENING:    frozenset({"ME", "JU"}),
    EventType.STOCK_INVESTMENT:        frozenset({"ME", "JU"}),
    EventType.CONTRACT_SIGNING:        frozenset({"ME", "JU"}),
    EventType.DEBT_PAYMENT:            frozenset({"SA", "MA"}),
    EventType.LOAN_APPLICATION:        frozenset({"SA"}),
    EventType.DIGITAL_LAUNCH:          frozenset({"ME", "JU"}),
    EventType.MERGER_ANNOUNCEMENT:     frozenset({"ME", "JU", "VE"}),
    EventType.INSURANCE_PURCHASE:      frozenset({"ME", "JU"}),
    # Category 5: Home & Domestic
    EventType.HOUSE_WARMING:           frozenset({"JU", "MO", "VE"}),
    EventType.HOUSE_SHIFTING:          frozenset({"JU", "MO"}),
    EventType.VEHICLE_PURCHASE:        frozenset({"ME", "VE"}),
    EventType.PET_ADOPTION:            frozenset({"MO", "JU", "VE"}),
    EventType.APPLIANCE_PURCHASE:      frozenset({"ME", "JU"}),
    EventType.KITCHEN_CEREMONY:        frozenset({"MO", "JU"}),
    # Category 6: Health, Travel & Legal
    EventType.LAWSUIT_FILING:          frozenset({"MA", "SU"}),
    EventType.TRAVEL:                  frozenset({"ME", "MO", "JU"}),
    EventType.INTERNATIONAL_TRAVEL:    frozenset({"ME", "JU"}),
    EventType.SURGERY:                 frozenset({"MA"}),
    EventType.MEDICAL_TREATMENT:       frozenset({"MO", "JU"}),
    EventType.DIVORCE_FILING:          frozenset({"SA", "MA"}),
    EventType.POST_ILLNESS_GROOMING:   frozenset({"MO", "JU"}),
    EventType.AYURVEDIC_TREATMENT:     frozenset({"MO", "JU"}),
    # Category 7: Spiritual & Shopping
    EventType.GOLD_PURCHASE:           frozenset({"SU", "JU"}),
    EventType.NEW_CLOTHES:             frozenset({"VE", "MO", "JU"}),
    EventType.IDOL_INSTALLATION:       frozenset({"JU", "MO"}),
    EventType.SPIRITUAL_INITIATION:    frozenset({"JU", "MO"}),
    EventType.VRATA_DIKSHA:            frozenset({"JU", "MO"}),
    EventType.CREATIVE_PROJECT:        frozenset({"VE", "ME"}),
    EventType.ANCESTRAL_RITUAL:        frozenset({"SA", "SU"}),
    # Category 8: Agriculture
    EventType.LAND_TILLING:            frozenset({"MA", "MO"}),
    EventType.CROP_SOWING:             frozenset({"MO", "JU"}),
    EventType.IRRIGATION_INSTALLATION: frozenset({"MO", "JU"}),
    EventType.CROP_HARVESTING:         frozenset({"MO", "JU", "VE"}),
    EventType.GRAIN_STORAGE:           frozenset({"JU", "MO"}),
}

# ---------------------------------------------------------------------------
# Tara Bala constants (9-star cycle from Janma Nakshatra)
# ---------------------------------------------------------------------------

_INAUSPICIOUS_TARAS: frozenset[int] = frozenset({3, 5, 7})   # Vipat, Pratyak, Naidhana
_TARA_NAMES: dict[int, str] = {
    1: "Janma", 2: "Sampat", 3: "Vipat", 4: "Kshema",
    5: "Pratyak", 6: "Sadhana", 7: "Naidhana", 8: "Mitra", 9: "Param Mitra",
}
_TARA_DESCRIPTIONS: dict[int, str] = {
    1: "Janma Tara — birth star cycle, neutral, be cautious",
    2: "Sampat Tara — prosperity and wealth, very auspicious",
    3: "Vipat Tara — danger and obstacles, avoid important activities",
    4: "Kshema Tara — well-being and comfort, auspicious",
    5: "Pratyak Tara — obstacles and opposition, inauspicious",
    6: "Sadhana Tara — achievement and success, auspicious",
    7: "Naidhana Tara — death-like energy, very inauspicious — avoid",
    8: "Mitra Tara — friendship and support, auspicious",
    9: "Param Mitra Tara — best friendship, highly auspicious",
}
_TARA_AUSPICIOUS: dict[int, bool] = {
    1: False, 2: True, 3: False, 4: True,
    5: False, 6: True, 7: False, 8: True, 9: True,
}

# Moon in 6th, 8th, or 12th house from birth Rashi = Chandra Ashtama
_ASHTAMA_HOUSES: frozenset[int] = frozenset({6, 8, 12})

# ---------------------------------------------------------------------------
# Combustion (Asta) thresholds — degrees within Sun that combust a planet
# ---------------------------------------------------------------------------

_COMBUST_DEGREES: dict[str, float] = {
    "JU": 11.0,   # Jupiter combust within 11° of Sun
    "VE": 8.0,    # Venus combust within 8° of Sun
    "MA": 17.0,   # Mars combust within 17°
    "ME": 14.0,   # Mercury combust within 14° (mean)
    "SA": 15.0,   # Saturn combust within 15°
    "MO": 12.0,   # Moon (rarely used but kept for reference)
}
# F2 events need strong Jupiter AND Venus (Formula 2 prerequisite)
_F2_EVENTS: frozenset[EventType] = frozenset({
    EventType.PLASTERING, EventType.WINDOW_INSTALLATION, EventType.FLOORING_INSTALLATION,
    EventType.RENOVATION, EventType.PAINTING, EventType.CONCEPTION, EventType.BABY_SHOWER,
    EventType.CHILDBIRTH_RITUAL, EventType.NAMING_CEREMONY, EventType.CRADLE_CEREMONY,
    EventType.FIRST_SOLID_FOOD, EventType.FIRST_HAIRCUT, EventType.EAR_PIERCING,
    EventType.MARRIAGE, EventType.GOLD_PURCHASE, EventType.NEW_CLOTHES,
    EventType.IDOL_INSTALLATION, EventType.SPIRITUAL_INITIATION, EventType.VRATA_DIKSHA,
    EventType.CREATIVE_PROJECT,
})

# ---------------------------------------------------------------------------
# Disha Shool — inauspicious travel direction by weekday
# Weekday 0=Mon..6=Sun (Python). Value = compass direction to AVOID.
# ---------------------------------------------------------------------------

_DISHA_SHOOL: dict[int, str] = {
    0: "east",   # Monday   → avoid East
    1: "north",  # Tuesday  → avoid North
    2: "north",  # Wednesday → avoid North
    3: "east",   # Thursday → avoid East
    4: "south",  # Friday   → avoid South
    5: "east",   # Saturday → avoid East (some texts say West)
    6: "west",   # Sunday   → avoid West
}
_TRAVEL_EVENTS: frozenset[EventType] = frozenset({
    EventType.TRAVEL, EventType.INTERNATIONAL_TRAVEL,
})

# ---------------------------------------------------------------------------
# Moon body-part rashi rule for surgery (Rashi 1-12 → body part)
# ---------------------------------------------------------------------------

_RASHI_BODY_PART: dict[int, str] = {
    1: "head",       2: "neck",        3: "arms",
    4: "chest",      5: "heart",       6: "abdomen",
    7: "kidneys",    8: "reproductive", 9: "thighs",
    10: "knees",     11: "calves",     12: "feet",
}

# ---------------------------------------------------------------------------
# Lagna (ascendant) favorable signs per formula group
# Signs 1=Aries..12=Pisces; Fixed={2,5,8,11}; Movable={1,4,7,10}; Dual={3,6,9,12}
# ---------------------------------------------------------------------------

_RASHI_NAMES: dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces",
}
_FIXED_LAGNA   = frozenset({2, 5, 8, 11})   # Taurus, Leo, Scorpio, Aquarius
_DUAL_LAGNA    = frozenset({3, 6, 9, 12})   # Gemini, Virgo, Sagittarius, Pisces
_MOVABLE_LAGNA = frozenset({1, 4, 7, 10})   # Aries, Cancer, Libra, Capricorn
_BENEFIC_LAGNA = frozenset({2, 3, 6, 7, 9, 12})  # Jupiter/Venus/Mercury ruled
_WATERY_EARTH_LAGNA = frozenset({2, 4, 6, 8, 10, 12})  # Agriculture/growth

# Map each event to the Lagna signs that are auspicious for it
_EVENT_FAVORABLE_LAGNA: dict[EventType, frozenset[int]] = {}

# Formula 1 — Fixed Lagna for permanence
_F1_LAGNA_EVENTS = {
    EventType.LAND_PURCHASE, EventType.GROUNDBREAKING, EventType.WELL_DIGGING,
    EventType.FOUNDATION_DIGGING, EventType.FOUNDATION_STONE, EventType.PILLAR_INSTALLATION,
    EventType.COLUMN_CASTING, EventType.BRICKWORK, EventType.DOOR_FRAME_INSTALLATION,
    EventType.ROOF_CASTING, EventType.STAIRCASE_CONSTRUCTION, EventType.BOUNDARY_WALL,
    EventType.PROPERTY_PURCHASE, EventType.CONSTRUCTION,
    EventType.HOUSE_WARMING, EventType.HOUSE_SHIFTING,
    EventType.MARRIAGE,  # marriage specifically uses Fixed Lagna
}
for _e in _F1_LAGNA_EVENTS:
    _EVENT_FAVORABLE_LAGNA[_e] = _FIXED_LAGNA

# Formula 2 — Benefic (Jupiter/Venus/Mercury) Lagna
for _e in _F2_EVENTS - {EventType.MARRIAGE}:  # marriage uses Fixed above
    _EVENT_FAVORABLE_LAGNA[_e] = _BENEFIC_LAGNA

# Formula 2 finishing construction uses Benefic Lagna
for _e in {EventType.PLASTERING, EventType.WINDOW_INSTALLATION,
           EventType.FLOORING_INSTALLATION, EventType.RENOVATION, EventType.PAINTING}:
    _EVENT_FAVORABLE_LAGNA[_e] = _BENEFIC_LAGNA

# Formula 3 — Dual/Mutable Lagna for speed and adaptability
for _e in {
    EventType.SACRED_THREAD, EventType.EDUCATION, EventType.PUBERTY_CEREMONY,
    EventType.SHASHTI_POORTHI, EventType.BHIMARATHA_SHANTHI, EventType.SADHABISHEKAM,
    EventType.JOB_JOINING, EventType.BUSINESS_START, EventType.BANK_ACCOUNT_OPENING,
    EventType.DIGITAL_LAUNCH, EventType.MERGER_ANNOUNCEMENT, EventType.INSURANCE_PURCHASE,
    EventType.VEHICLE_PURCHASE, EventType.PET_ADOPTION, EventType.APPLIANCE_PURCHASE,
    EventType.KITCHEN_CEREMONY, EventType.DIVORCE_FILING,
}:
    _EVENT_FAVORABLE_LAGNA[_e] = _DUAL_LAGNA

# Formula 4 — Surgery/Legal → Movable; Healing → Fixed; Travel → Movable
for _e in {EventType.LAWSUIT_FILING, EventType.INTERNATIONAL_TRAVEL}:
    _EVENT_FAVORABLE_LAGNA[_e] = _MOVABLE_LAGNA
for _e in {EventType.SURGERY, EventType.STOCK_INVESTMENT, EventType.CONTRACT_SIGNING,
           EventType.DEBT_PAYMENT, EventType.LOAN_APPLICATION}:
    _EVENT_FAVORABLE_LAGNA[_e] = _MOVABLE_LAGNA
for _e in {EventType.MEDICAL_TREATMENT, EventType.POST_ILLNESS_GROOMING, EventType.AYURVEDIC_TREATMENT}:
    _EVENT_FAVORABLE_LAGNA[_e] = _FIXED_LAGNA
for _e in {EventType.TRAVEL}:
    _EVENT_FAVORABLE_LAGNA[_e] = _MOVABLE_LAGNA

# Formula 5 — Watery/Earth Lagna for growth and fertility
for _e in {
    EventType.LAND_TILLING, EventType.CROP_SOWING, EventType.IRRIGATION_INSTALLATION,
    EventType.CROP_HARVESTING, EventType.GRAIN_STORAGE,
}:
    _EVENT_FAVORABLE_LAGNA[_e] = _WATERY_EARTH_LAGNA

# Sampling interval for Lagna sweep on single-day queries
_LAGNA_SAMPLE_MINUTES = 20

# ---------------------------------------------------------------------------
# Internal service dataclasses (not exported — see ndastro_api.core.models.muhurta)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _TimingWindows:
    """Sunrise-dependent timing windows computed lazily for top-N results only."""

    abhijit_muhurta: TimeWindowSummary | None
    rahu_kalam: TimeWindowSummary | None
    yamagandam: TimeWindowSummary | None
    gulika: TimeWindowSummary | None
    amrita_kala: tuple[TimeWindowSummary, ...]
    sunrise: str | None
    sunset: str | None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search_auspicious_dates(
    *,
    start_date: date,
    end_date: date,
    lat: float,
    lon: float,
    ayanamsa_system: AyanamsaSystem,
    event: EventType,
    min_score: float | None = None,
    limit: int = 30,
    janma_nakshatra: int | None = None,
    birth_rashi: int | None = None,
    travel_direction: str | None = None,
    surgery_body_part: str | None = None,
) -> tuple[AuspiciousDateResult, ...]:
    """Scan a date range and return dates most auspicious for the given event.

    Args:
        start_date: First date of the search window (inclusive).
        end_date: Last date of the search window (inclusive).
        lat: Geographic latitude.
        lon: Geographic longitude.
        ayanamsa_system: Ayanamsa system to use for planetary positions.
        event: Life event for which auspicious dates are sought.
        min_score: If set, only include dates scoring at or above this value.
        limit: Maximum number of results to return (1-100).
        janma_nakshatra: Birth nakshatra 1-27; enables Tara Bala check.
        birth_rashi: Birth Moon sign 1-12; enables Chandra Ashtama check.
        travel_direction: Intended travel direction (north/south/east/west); enables Disha Shool check.
        surgery_body_part: Body part being operated (head/neck/arms/chest/etc.); enables Moon body-part caution.

    Returns:
        Tuple of AuspiciousDateResult, sorted by score descending.

    """
    if end_date < start_date:
        msg = "end_date must be on or after start_date"
        raise ValueError(msg)

    total_days = (end_date - start_date).days + 1
    if total_days > MAX_DATE_RANGE_DAYS:
        msg = f"Date range must not exceed {MAX_DATE_RANGE_DAYS} days (got {total_days})"
        raise ValueError(msg)

    effective_limit = min(max(1, limit), MAX_RESULTS)
    criteria = _EVENT_CRITERIA.get(event)

    dates: list[date] = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)

    def _eval(d: date) -> AuspiciousDateResult | None:
        return _evaluate_date_cached(d, lat, lon, str(ayanamsa_system), event.value)

    # Phase 1 — score every day cheaply (no sunrise/sunset).
    results: list[AuspiciousDateResult] = []
    for d in dates:
        result = _eval(d)
        if result is not None and (min_score is None or result.score >= min_score):
            results.append(result)

    results.sort(key=lambda r: r.score, reverse=True)
    top = results[:effective_limit]

    # Phase 2 — enrich only the top-N with timing windows (Rahu Kalam, Abhijit, etc.).
    # This limits the expensive get_sunrise_sunset calls to at most `limit` instead of
    # every day in the range.
    enriched = tuple(_enrich_timing(r, lat, lon, janma_nakshatra, birth_rashi, travel_direction, surgery_body_part) for r in top)

    # Phase 3 — Lagna windows only when the query is a single day.
    if start_date == end_date:
        enriched = tuple(
            dc_replace(r, lagna_windows=_compute_lagna_windows(
                start_date, lat, lon, str(ayanamsa_system), r.event,
            ))
            for r in enriched
        )

    return enriched


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

@lru_cache(maxsize=2048)
def _evaluate_date_cached(
    d: date,
    lat: float,
    lon: float,
    ayanamsa_system_str: str,
    event_value: str,
) -> AuspiciousDateResult | None:
    """Cached per-day evaluation — keyed on (date, lat, lon, ayanamsa, event).

    Results are deterministic for a given set of inputs, so repeated calls
    with the same parameters (e.g. repeated API requests) return instantly.
    AyanamsaSystem is a Literal TypeAlias (not a class), so we pass the raw
    string directly — get_ayanamsa accepts string values.
    """
    event = EventType(event_value)
    criteria = _EVENT_CRITERIA.get(event)
    dt = datetime(d.year, d.month, d.day, 6, 0, 0, tzinfo=UTC)
    with contextlib.suppress(Exception):
        return _compute_result(
            dt,
            lat=lat,
            lon=lon,
            ayanamsa_system=ayanamsa_system_str,  # type: ignore[arg-type]
            event=event,
            criteria=criteria,
        )
    return None


@lru_cache(maxsize=2048)
def _compute_timing_windows_cached(d: date, lat: float, lon: float, moon_nak: int) -> _TimingWindows:
    """Compute sunrise-dependent timing windows. Cached by (date, lat, lon, nakshatra)."""
    dt = datetime(d.year, d.month, d.day, 6, 0, 0, tzinfo=UTC)
    sr: datetime | None = None
    ss: datetime | None = None
    with contextlib.suppress(Exception):
        sr, ss = get_sunrise_sunset(lat, lon, dt)

    rahu_kalam = yamagandam = gulika = abhijit = None
    amrita_kala: tuple[TimeWindowSummary, ...] = ()
    if sr and ss:
        with contextlib.suppress(Exception):
            rahu_kalam = _summarize(get_rahu_kalam(sunrise=sr, sunset=ss, date_value=dt))
        with contextlib.suppress(Exception):
            yamagandam = _summarize(get_yamagandam(sunrise=sr, sunset=ss, date_value=dt))
        with contextlib.suppress(Exception):
            gulika = _summarize(get_gulika(sunrise=sr, sunset=ss, date_value=dt))
        with contextlib.suppress(Exception):
            ab = get_abhijit_muhurta(sunrise=sr, sunset=ss, date_value=dt)
            abhijit = _summarize(ab) if ab else None
        with contextlib.suppress(Exception):
            weekday_vedic = (d.weekday() + 1) % 7  # Python Mon=0 → Vedic 1; Sun=6 → Vedic 0
            amrita_raw, _ = get_amrita_kala_windows(weekday_vedic, moon_nak, sr, ss)
            amrita_kala = tuple(s for s in (_summarize_amrita(a) for a in amrita_raw) if s is not None)

    return _TimingWindows(
        abhijit_muhurta=abhijit,
        rahu_kalam=rahu_kalam,
        yamagandam=yamagandam,
        gulika=gulika,
        amrita_kala=amrita_kala,
        sunrise=sr.isoformat() if sr else None,
        sunset=ss.isoformat() if ss else None,
    )


def _enrich_timing(
    result: AuspiciousDateResult,
    lat: float,
    lon: float,
    janma_nakshatra: int | None = None,
    birth_rashi: int | None = None,
    travel_direction: str | None = None,
    surgery_body_part: str | None = None,
) -> AuspiciousDateResult:
    """Attach timing windows, horas, Tara Bala, Chandra Ashtama, Disha Shool, and Moon-body-part caution."""
    d = date.fromisoformat(result.date)
    tw = _compute_timing_windows_cached(d, lat, lon, result.nakshatra)

    favorable_horas = _calculate_favorable_horas(d, tw.sunrise, result.event)

    tara_bala: TaraResult | None = None
    if janma_nakshatra is not None:
        tara_bala = _calculate_tara_bala(janma_nakshatra, result.nakshatra)

    chandra_ashtama: bool | None = None
    chandra_ashtama_house: int | None = None
    if birth_rashi is not None:
        chandra_ashtama_house = (result.moon_rashi - birth_rashi) % 12 + 1
        chandra_ashtama = chandra_ashtama_house in _ASHTAMA_HOUSES

    # Disha Shool — only relevant for travel events
    disha_shool_direction: str | None = None
    disha_shool_conflict: bool | None = None
    if result.event in {EventType.TRAVEL.value, EventType.INTERNATIONAL_TRAVEL.value}:
        weekday = d.weekday()
        disha_shool_direction = _DISHA_SHOOL.get(weekday)
        if travel_direction and disha_shool_direction:
            disha_shool_conflict = travel_direction.lower().strip() == disha_shool_direction

    # Moon body-part rule for surgery
    moon_body_part: str | None = None
    # Lagna windows (only populated for single-day queries)
    lagna_windows: tuple[LagnaWindow, ...] = ()
    if result.event == EventType.SURGERY.value and surgery_body_part:
        moon_part = _RASHI_BODY_PART.get(result.moon_rashi, "")
        if moon_part and surgery_body_part.lower().strip() == moon_part:
            moon_body_part = moon_part

    # Build updated reasons/cautions (extend existing lists)
    extra_reasons: list[str] = []
    extra_cautions: list[str] = []

    if result.jupiter_combust and result.event in {e.value for e in _F2_EVENTS}:
        extra_cautions.append("Jupiter is combust (Asta) — weakened blessing; avoid if possible")
    if result.venus_combust and result.event in {e.value for e in _F2_EVENTS}:
        extra_cautions.append("Venus is combust (Asta) — weakened beauty/harmony energy")
    if disha_shool_conflict:
        extra_cautions.append(f"Disha Shool: travelling {travel_direction} is inauspicious on {d.strftime('%A')} — avoid or perform a remedial puja")
    elif disha_shool_direction and travel_direction and not disha_shool_conflict:
        extra_reasons.append(f"Disha Shool: {travel_direction} direction is safe on {d.strftime('%A')}")
    if moon_body_part:
        extra_cautions.append(f"Moon is transiting {_RASHI_BODY_PART.get(result.moon_rashi, 'unknown')} rashi — avoid operating on {moon_body_part} today")

    updated_reasons = list(result.supporting_reasons) + extra_reasons
    updated_cautions = list(result.caution_reasons) + extra_cautions

    return dc_replace(
        result,
        supporting_reasons=updated_reasons,
        caution_reasons=updated_cautions,
        amrita_kala=tw.amrita_kala,
        favorable_horas=tuple(favorable_horas),
        tara_bala=tara_bala,
        chandra_ashtama=chandra_ashtama,
        chandra_ashtama_house=chandra_ashtama_house,
        disha_shool_direction=disha_shool_direction,
        disha_shool_conflict=disha_shool_conflict,
        moon_body_part=moon_body_part,
        abhijit_muhurta=tw.abhijit_muhurta,
        rahu_kalam=tw.rahu_kalam,
        yamagandam=tw.yamagandam,
        gulika=tw.gulika,
        sunrise=tw.sunrise,
        sunset=tw.sunset,
    )


def _evaluate_date(
    d: date,
    *,
    lat: float,
    lon: float,
    ayanamsa_system: AyanamsaSystem,
    event: EventType,
    criteria: _EventCriteria | None,
) -> AuspiciousDateResult | None:
    dt = datetime(d.year, d.month, d.day, 6, 0, 0, tzinfo=UTC)
    with contextlib.suppress(Exception):
        return _compute_result(dt, lat=lat, lon=lon, ayanamsa_system=ayanamsa_system, event=event, criteria=criteria)
    return None


def _compute_result(
    dt: datetime,
    *,
    lat: float,
    lon: float,
    ayanamsa_system: AyanamsaSystem,
    event: EventType,
    criteria: _EventCriteria | None,
) -> AuspiciousDateResult:
    ayan = get_ayanamsa(dt, ayanamsa_system)

    # Only compute Sun and Moon — all other planets are not needed for panchanga scoring.
    # This reduces per-day Skyfield calls from ~22 (all planets + retrograde) to 2.
    sun_pos = get_planet_position(Planets.SUN, lat, lon, dt)
    moon_pos = get_planet_position(Planets.MOON, lat, lon, dt)
    sun_lon = normalize_degree(sun_pos.longitude - ayan)
    moon_lon = normalize_degree(moon_pos.longitude - ayan)
    moon_nak_code, _ = get_nakshatra_and_pada(moon_lon)
    moon_nak = int(moon_nak_code[1:])        # "N04" → 4
    moon_rashi = int(moon_lon / 30) % 12 + 1  # 1-12 (Aries=1..Pisces=12)

    # Jupiter & Venus combustion — only computed for F2 events (adds 2 Skyfield calls).
    jupiter_combust = False
    venus_combust = False
    if event in _F2_EVENTS:
        with contextlib.suppress(Exception):
            ju_pos = get_planet_position(Planets.JUPITER, lat, lon, dt)
            ju_lon = normalize_degree(ju_pos.longitude - ayan)
            jupiter_combust = _is_combust(sun_lon, ju_lon, _COMBUST_DEGREES["JU"])
        with contextlib.suppress(Exception):
            ve_pos = get_planet_position(Planets.VENUS, lat, lon, dt)
            ve_lon = normalize_degree(ve_pos.longitude - ayan)
            venus_combust = _is_combust(sun_lon, ve_lon, _COMBUST_DEGREES["VE"])

    panchanga_data = get_panchanga_with_data(sun_lon, moon_lon, date_value=dt)
    activity_key = criteria.activity_key if criteria else event.value.replace("_", " ")
    activity_support = get_activity_support(panchanga_data, activity=activity_key)

    score = _compute_score(panchanga_data, moon_nak, criteria, jupiter_combust, venus_combust, event)
    reasons, cautions = _build_reasons(panchanga_data, activity_support, moon_nak, criteria, activity_key)

    # Timing windows (rahu_kalam, sunrise, etc.) are NOT computed here.
    # They are populated lazily by _enrich_timing() only for the top-N results.
    p = panchanga_data.panchanga
    return AuspiciousDateResult(
        date=dt.date().isoformat(),
        event=event.value,
        score=round(score, 2),
        tithi_number=p.tithi.number,
        tithi_name=p.tithi.name,
        paksha=p.tithi.paksha,
        vara_number=p.vara.number,
        vara_name=p.vara.name,
        nakshatra=moon_nak,
        moon_rashi=moon_rashi,
        yoga_name=p.yoga_name,
        yoga_number=p.yoga_number,
        muhurta_rating=panchanga_data.muhurta_rating,
        tithi_support=activity_support.tithi_support,
        karana_support=activity_support.karana_support,
        vara_support=activity_support.vara_support,
        yoga_support=activity_support.yoga_support,
        inauspicious_flags=list(activity_support.inauspicious_flags),
        supporting_reasons=reasons,
        caution_reasons=cautions,
        abhijit_muhurta=None,
        rahu_kalam=None,
        yamagandam=None,
        gulika=None,
        sunrise=None,
        sunset=None,
        jupiter_combust=jupiter_combust,
        venus_combust=venus_combust,
    )


def _compute_score(
    panchanga_data: PanchangaDataResult,
    nakshatra: int,
    criteria: _EventCriteria | None,
    jupiter_combust: bool = False,
    venus_combust: bool = False,
    event: EventType | None = None,
) -> float:
    base = float(panchanga_data.muhurta_rating or 5.0)

    if criteria is None:
        return base

    p = panchanga_data.panchanga
    tithi_score = (
        2.0 if p.tithi.number in criteria.good_tithis
        else (-2.0 if p.tithi.number in criteria.bad_tithis else 0.0)
    )
    vara_score = (
        2.0 if p.vara.number in criteria.good_varas
        else (-2.0 if p.vara.number in criteria.bad_varas else 0.0)
    )
    nakshatra_score = 2.0 if nakshatra in criteria.good_nakshatras else 0.0
    paksha_bonus = 0.5 if p.tithi.paksha == "shukla" else 0.0

    # Combustion penalty for Formula-2 events: -1 per combust benefic
    combust_penalty = 0.0
    if event in _F2_EVENTS:
        if jupiter_combust:
            combust_penalty -= 1.0
        if venus_combust:
            combust_penalty -= 1.0

    return max(0.0, base + tithi_score + vara_score + nakshatra_score + paksha_bonus + combust_penalty)


def _build_reasons(
    panchanga_data: PanchangaDataResult,
    activity_support: PanchangaActivitySupport,
    nakshatra: int,
    criteria: _EventCriteria | None,
    activity_key: str,
) -> tuple[list[str], list[str]]:
    reasons: list[str] = []
    cautions: list[str] = []

    p = panchanga_data.panchanga
    tithi = p.tithi
    vara = p.vara

    if criteria:
        if tithi.number in criteria.good_tithis:
            reasons.append(f"Tithi {tithi.name} ({tithi.number}) is auspicious for {activity_key}")
        elif tithi.number in criteria.bad_tithis:
            cautions.append(f"Tithi {tithi.name} ({tithi.number}) is inauspicious for {activity_key}")

        if vara.number in criteria.good_varas:
            reasons.append(f"Vara ({vara.name}) is favorable for {activity_key}")
        elif vara.number in criteria.bad_varas:
            cautions.append(f"Vara ({vara.name}) is unfavorable for {activity_key}")

        if nakshatra in criteria.good_nakshatras:
            reasons.append(f"Nakshatra {nakshatra} is auspicious for {activity_key}")

    if tithi.paksha == "shukla":
        reasons.append("Shukla Paksha (waxing Moon) — favorable for new beginnings")
    else:
        cautions.append("Krishna Paksha (waning Moon) — Shukla Paksha preferred for important events")

    if tithi.number in (4, 9, 14):
        cautions.append(f"Rikta tithi ({tithi.name}) — generally avoid for auspicious works")

    for flag in activity_support.inauspicious_flags:
        cautions.append(f"{flag.capitalize()} element is inauspicious for {activity_key}")

    return reasons, cautions


@lru_cache(maxsize=512)
def _compute_lagna_windows(
    d: date,
    lat: float,
    lon: float,
    ayanamsa_system_str: str,
    event_value: str,
) -> tuple[LagnaWindow, ...]:
    """Sweep the ascendant every _LAGNA_SAMPLE_MINUTES through the day and return
    contiguous windows per rashi.  Only called for single-day queries.
    """
    favorable = _EVENT_FAVORABLE_LAGNA.get(EventType(event_value), frozenset())
    dt_start = datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=UTC)

    # Pre-compute ayanamsa once for the day (barely changes within 24 h)
    ayan = get_ayanamsa(dt_start, ayanamsa_system_str)  # type: ignore[arg-type]

    # Sample the Lagna at regular intervals
    samples: list[tuple[datetime, int]] = []
    step = timedelta(minutes=_LAGNA_SAMPLE_MINUTES)
    current = dt_start
    end_of_day = dt_start + timedelta(hours=24)
    while current < end_of_day:
        with contextlib.suppress(Exception):
            trop_asc = get_ascendent_position(lat, lon, current)
            sidereal_asc = normalize_degree(trop_asc - ayan)
            rashi = int(sidereal_asc / 30) % 12 + 1  # 1-12
            samples.append((current, rashi))
        current += step

    if not samples:
        return ()

    # Merge consecutive same-rashi intervals
    windows: list[LagnaWindow] = []
    seg_start, seg_rashi = samples[0]
    for i in range(1, len(samples)):
        ts_curr, rashi_curr = samples[i]
        if rashi_curr != seg_rashi:
            seg_end = samples[i][0]
            dur = (seg_end - seg_start).total_seconds() / 60.0
            windows.append(LagnaWindow(
                sign_number=seg_rashi,
                sign_name=_RASHI_NAMES.get(seg_rashi, str(seg_rashi)),
                is_favorable=seg_rashi in favorable,
                start=seg_start.isoformat(),
                end=seg_end.isoformat(),
                duration_minutes=round(dur, 1),
            ))
            seg_start, seg_rashi = ts_curr, rashi_curr
    # Final segment
    seg_end = dt_start + timedelta(hours=24)
    dur = (seg_end - seg_start).total_seconds() / 60.0
    windows.append(LagnaWindow(
        sign_number=seg_rashi,
        sign_name=_RASHI_NAMES.get(seg_rashi, str(seg_rashi)),
        is_favorable=seg_rashi in favorable,
        start=seg_start.isoformat(),
        end=seg_end.isoformat(),
        duration_minutes=round(dur, 1),
    ))

    return tuple(windows)


def _is_combust(sun_lon: float, planet_lon: float, threshold_deg: float) -> bool:
    """Return True if planet is within threshold_deg of Sun (angular arc ≤ threshold)."""
    arc = abs(sun_lon - planet_lon) % 360.0
    if arc > 180.0:
        arc = 360.0 - arc
    return arc <= threshold_deg


def _summarize_amrita(aw: AmritaKalaWindow) -> TimeWindowSummary | None:
    """Convert an AmritaKalaWindow to a TimeWindowSummary (quality becomes the name)."""
    tw = aw.window
    if tw.start is None or tw.end is None:
        return None
    dur = (tw.end - tw.start).total_seconds() / 60.0
    return TimeWindowSummary(
        name=aw.quality,
        start=tw.start.isoformat(),
        end=tw.end.isoformat(),
        duration_minutes=round(dur, 2),
    )


def _calculate_favorable_horas(
    d: date,
    sunrise_str: str | None,
    event_value: str,
) -> list[HoraWindow]:
    """Return planetary hora slots (1-hour windows from sunrise) that match the event."""
    if sunrise_str is None:
        return []
    try:
        sunrise_dt = datetime.fromisoformat(sunrise_str)
    except ValueError:
        return []
    try:
        favorable_lords = _EVENT_FAVORABLE_HORA_LORDS.get(EventType(event_value), frozenset())
    except ValueError:
        return []
    if not favorable_lords:
        return []

    start_idx = _DAY_HORA_START_IDX[d.weekday()]
    hora_td = timedelta(hours=1)
    windows: list[HoraWindow] = []
    for hora_num in range(24):
        lord_code = _CHALDEAN_ORDER[(start_idx + hora_num) % 7]
        if lord_code not in favorable_lords:
            continue
        start = sunrise_dt + hora_td * hora_num
        end = start + hora_td
        windows.append(HoraWindow(
            hora_number=hora_num + 1,
            lord_code=lord_code,
            lord_name=_CHALDEAN_NAMES[lord_code],
            start=start.isoformat(),
            end=end.isoformat(),
            duration_minutes=60.0,
        ))
    return windows


def _calculate_tara_bala(janma_nakshatra: int, current_nakshatra: int) -> TaraResult:
    """Compute Tara Bala from birth nakshatra and current Moon nakshatra."""
    count = ((current_nakshatra - janma_nakshatra) % 27) + 1   # 1-27
    tara_num = ((count - 1) % 9) + 1                            # 1-9
    return TaraResult(
        tara_number=tara_num,
        tara_name=_TARA_NAMES[tara_num],
        is_auspicious=_TARA_AUSPICIOUS[tara_num],
        description=_TARA_DESCRIPTIONS[tara_num],
    )


def _summarize(tw: Any) -> TimeWindowSummary | None:
    if tw is None:
        return None
    start = getattr(tw, "start", None)
    end = getattr(tw, "end", None)
    name = getattr(tw, "name", "")
    if start is None or end is None:
        return None
    dur = (end - start).total_seconds() / 60.0
    return TimeWindowSummary(
        name=str(name),
        start=start.isoformat(),
        end=end.isoformat(),
        duration_minutes=round(dur, 2),
    )
