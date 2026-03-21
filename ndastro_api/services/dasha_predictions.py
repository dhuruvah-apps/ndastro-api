"""Dasha Predictions & Interpretations Module.

Provides comprehensive predictions and interpretations for Vimsottari Dasha periods.
Analyzes planetary periods (Mahadasha, Antardasha) based on:
- Natural significations
- House lordship and placement
- Planetary strength and dignity
- Aspects and yogas
- Combined effects in sub-periods
- Life area predictions (career, finance, relationships, health)
- Event timing and recommendations
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# Natural significations of planets
PLANET_SIGNIFICATIONS = {
    "sun": {
        "natural_significations": [
            "Soul",
            "Father",
            "Authority",
            "Government",
            "Leadership",
            "Vitality",
            "Confidence",
            "Status",
            "Power",
            "Politics",
            "Administration",
            "Health",
            "Heart",
            "Eyes",
        ],
        "positive_traits": ["Strong willpower", "Leadership qualities", "Recognition", "Success", "Authority"],
        "negative_traits": ["Ego issues", "Conflicts with authority", "Health problems", "Pride", "Burnout"],
        "career_domains": ["Government", "Politics", "Administration", "Leadership roles", "Medicine", "Pharmacy"],
        "health_areas": ["Heart", "Eyes", "Bone structure", "Vitality", "Immunity"],
    },
    "moon": {
        "natural_significations": [
            "Mind",
            "Emotions",
            "Mother",
            "Comfort",
            "Intuition",
            "Memory",
            "Public",
            "Home",
            "Water",
            "Travel",
            "Flexibility",
            "Care",
            "Nourishment",
        ],
        "positive_traits": ["Emotional fulfillment", "Public recognition", "Travel", "Comfort", "Family happiness"],
        "negative_traits": ["Emotional instability", "Anxiety", "Mood swings", "Restlessness", "Overthinking"],
        "career_domains": ["Hospitality", "Nursing", "Public relations", "Marine", "Food industry", "Tourism"],
        "health_areas": ["Mind", "Stomach", "Breasts", "Fluids", "Mental health"],
    },
    "mars": {
        "natural_significations": [
            "Energy",
            "Courage",
            "Action",
            "Brothers",
            "Land",
            "Property",
            "Weapons",
            "Sports",
            "Surgery",
            "Police",
            "Military",
            "Competition",
            "Aggression",
        ],
        "positive_traits": ["Courage", "Initiative", "Energy", "Achievement", "Competitive success"],
        "negative_traits": ["Accidents", "Conflicts", "Aggression", "Impulsiveness", "Legal issues"],
        "career_domains": ["Military", "Police", "Engineering", "Surgery", "Sports", "Real estate"],
        "health_areas": ["Blood", "Muscles", "Energy levels", "Accidents", "Inflammations"],
    },
    "mercury": {
        "natural_significations": [
            "Intelligence",
            "Communication",
            "Business",
            "Education",
            "Speech",
            "Writing",
            "Trade",
            "Mathematics",
            "Accounts",
            "Friends",
            "Wit",
            "Learning",
        ],
        "positive_traits": ["Intellectual growth", "Business success", "Communication skills", "Learning", "Networking"],
        "negative_traits": ["Mental stress", "Communication issues", "Business losses", "Confusion", "Nervousness"],
        "career_domains": ["Business", "Commerce", "Writing", "Teaching", "Accounting", "IT", "Media"],
        "health_areas": ["Nervous system", "Speech", "Skin", "Respiratory system"],
    },
    "jupiter": {
        "natural_significations": [
            "Wisdom",
            "Expansion",
            "Wealth",
            "Children",
            "Guru",
            "Religion",
            "Philosophy",
            "Fortune",
            "Higher education",
            "Law",
            "Ethics",
            "Optimism",
        ],
        "positive_traits": ["Prosperity", "Spiritual growth", "Good fortune", "Knowledge", "Children's welfare"],
        "negative_traits": ["Over-optimism", "Weight gain", "Complacency", "Legal complications", "Excess"],
        "career_domains": ["Teaching", "Law", "Banking", "Finance", "Religious work", "Counseling", "Consultancy"],
        "health_areas": ["Liver", "Fat", "Thighs", "Overall well-being"],
    },
    "venus": {
        "natural_significations": [
            "Love",
            "Marriage",
            "Beauty",
            "Luxury",
            "Arts",
            "Vehicles",
            "Comfort",
            "Spouse",
            "Pleasure",
            "Romance",
            "Creativity",
            "Wealth",
        ],
        "positive_traits": [
            "Romantic fulfillment",
            "Material comforts",
            "Artistic success",
            "Marriage",
            "Luxury",
        ],
        "negative_traits": ["Over-indulgence", "Relationship issues", "Laziness", "Financial extravagance"],
        "career_domains": ["Arts", "Fashion", "Entertainment", "Hospitality", "Jewelry", "Beauty industry"],
        "health_areas": ["Reproductive system", "Kidneys", "Skin", "Sexual health"],
    },
    "saturn": {
        "natural_significations": [
            "Discipline",
            "Hard work",
            "Delays",
            "Karma",
            "Service",
            "Longevity",
            "Old age",
            "Sorrow",
            "Renunciation",
            "Labor",
            "Justice",
            "Structure",
        ],
        "positive_traits": ["Discipline", "Hard work paying off", "Stability", "Long-term success", "Maturity"],
        "negative_traits": ["Delays", "Obstacles", "Depression", "Losses", "Health issues", "Isolation"],
        "career_domains": ["Labor", "Mining", "Construction", "Agriculture", "Service sector", "Administration"],
        "health_areas": ["Bones", "Teeth", "Nerves", "Chronic diseases", "Joints"],
    },
    "rahu": {
        "natural_significations": [
            "Materialism",
            "Obsession",
            "Foreign",
            "Technology",
            "Innovation",
            "Deception",
            "Ambition",
            "Unconventional",
            "Sudden events",
            "Research",
        ],
        "positive_traits": ["Material success", "Foreign connections", "Innovation", "Research breakthrough", "Fame"],
        "negative_traits": ["Deception", "Confusion", "Addictions", "Sudden losses", "Unethical behavior"],
        "career_domains": ["Technology", "Foreign trade", "Research", "Unconventional fields", "Politics"],
        "health_areas": ["Mental confusion", "Addictions", "Allergies", "Toxic conditions"],
    },
    "kethu": {
        "natural_significations": [
            "Spirituality",
            "Detachment",
            "Liberation",
            "Occult",
            "Research",
            "Losses",
            "Isolation",
            "Enlightenment",
            "Past karma",
            "Mysticism",
        ],
        "positive_traits": ["Spiritual growth", "Detachment", "Occult knowledge", "Liberation", "Insight"],
        "negative_traits": ["Losses", "Isolation", "Confusion", "Health issues", "Lack of direction"],
        "career_domains": ["Spirituality", "Occult", "Research", "Computers", "Technical fields"],
        "health_areas": ["Mysterious diseases", "Mental disturbances", "Nervous disorders"],
    },
}

# House significations for lordship analysis
HOUSE_SIGNIFICATIONS = {
    1: {"areas": ["Self", "Body", "Personality", "Health", "Vitality"], "nature": "Trine (Trikona)"},
    2: {"areas": ["Wealth", "Family", "Speech", "Food", "Values"], "nature": "Neutral"},
    3: {"areas": ["Courage", "Siblings", "Communication", "Short travels", "Efforts"], "nature": "Upachaya"},
    4: {"areas": ["Mother", "Home", "Comfort", "Education", "Property", "Heart"], "nature": "Kendra"},
    5: {"areas": ["Children", "Intelligence", "Creativity", "Romance", "Speculation"], "nature": "Trine (Trikona)"},
    6: {"areas": ["Enemies", "Disease", "Debt", "Service", "Competition"], "nature": "Dusthana"},
    7: {"areas": ["Marriage", "Partnership", "Business", "Spouse", "Travel"], "nature": "Kendra"},
    8: {
        "areas": ["Transformation", "Longevity", "Occult", "Inheritance", "Hidden matters"],
        "nature": "Dusthana",
    },
    9: {"areas": ["Father", "Fortune", "Religion", "Higher learning", "Long travels"], "nature": "Trine (Trikona)"},
    10: {"areas": ["Career", "Status", "Reputation", "Authority", "Achievements"], "nature": "Kendra"},
    11: {"areas": ["Gains", "Income", "Friends", "Aspirations", "Elder siblings"], "nature": "Upachaya"},
    12: {"areas": ["Loss", "Expenses", "Foreign", "Liberation", "Isolation", "Sleep"], "nature": "Dusthana"},
}

# House number constants for clarity
HOUSE_1_SELF = 1
HOUSE_2_WEALTH = 2
HOUSE_3_SIBLINGS = 3
HOUSE_4_HOME = 4
HOUSE_5_CHILDREN = 5
HOUSE_6_ENEMIES = 6
HOUSE_7_MARRIAGE = 7
HOUSE_8_TRANSFORMATION = 8
HOUSE_9_FORTUNE = 9
HOUSE_10_CAREER = 10
HOUSE_11_GAINS = 11
HOUSE_12_LOSS = 12

# Strength score thresholds
STRENGTH_VERY_STRONG_THRESHOLD = 8
STRENGTH_STRONG_THRESHOLD = 5
STRENGTH_MODERATE_THRESHOLD = 2
STRENGTH_WEAK_THRESHOLD = -1


# Life area categories for predictions
class LifeArea(str, Enum):
    """Major life areas for dasha predictions."""

    CAREER = "career"
    FINANCE = "finance"
    RELATIONSHIPS = "relationships"
    HEALTH = "health"
    EDUCATION = "education"
    SPIRITUALITY = "spirituality"
    FAMILY = "family"
    TRAVEL = "travel"


class PredictionStrength(str, Enum):
    """Strength of prediction/effect."""

    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    VERY_WEAK = "very_weak"


class EventTiming(str, Enum):
    """When events are likely during dasha period."""

    EARLY = "early"  # First 1/3 of period
    MIDDLE = "middle"  # Middle 1/3
    LATE = "late"  # Last 1/3
    THROUGHOUT = "throughout"  # Throughout period


@dataclass
class DashaPrediction:
    """Comprehensive prediction for a dasha period."""

    dasha_lord: str
    dasha_level: str  # maha, bhukti, antara
    general_theme: str
    positive_effects: list[str]
    negative_effects: list[str]
    life_area_predictions: dict[str, str]  # LifeArea -> prediction
    recommended_actions: list[str]
    things_to_avoid: list[str]
    favorable_activities: list[str]
    strength: PredictionStrength
    key_events_timing: dict[str, EventTiming]  # Event type -> timing


@dataclass
class BhuktiPrediction:
    """Combined prediction for Mahadasha + Bhukti (sub-period)."""

    maha_lord: str
    bhukti_lord: str
    combined_theme: str
    harmony_level: str  # "Excellent", "Good", "Neutral", "Challenging", "Difficult"
    dominant_planet: str  # Which planet's effects are stronger
    specific_predictions: list[str]
    optimal_activities: list[str]
    cautions: list[str]


@dataclass
class DignityStatus:
    """Planetary dignity status flags."""

    is_exalted: bool = False
    is_debilitated: bool = False
    is_retrograde: bool = False


@dataclass
class DashaContext:
    """Context for dasha prediction calculation."""

    planet: str
    houses_owned: list[int]
    house_placed: int
    dasha_level: str = "maha"
    is_exalted: bool = False
    is_debilitated: bool = False
    is_retrograde: bool = False


def get_planet_natural_effects(planet: str) -> dict:
    """Get natural significations and effects of a planet.

    Args:
        planet: Planet name (sun, moon, mars, etc.)

    Returns:
        Dictionary with natural significations, traits, domains

    """
    return PLANET_SIGNIFICATIONS.get(planet, {})


def interpret_house_lordship(planet: str, houses_owned: list[int]) -> dict[str, list[str]]:
    """Interpret effects of planet as lord of specific houses.

    Args:
        planet: Planet name
        houses_owned: List of house numbers the planet owns

    Returns:
        Dictionary with positive and negative lordship effects

    """
    positive_effects = []
    negative_effects = []

    for house in houses_owned:
        house_info = HOUSE_SIGNIFICATIONS.get(house, {})
        areas = house_info.get("areas", [])
        nature = house_info.get("nature", "")

        # Trikona lords (1, 5, 9) are always beneficial
        if nature == "Trine (Trikona)":
            positive_effects.append(f"{planet.title()} as lord of {house}th house brings fortune in: {', '.join(areas)}")

        # Kendra lords (1, 4, 7, 10) are generally beneficial
        elif nature == "Kendra":
            positive_effects.append(f"{planet.title()} as lord of {house}th house supports: {', '.join(areas)}")

        # Upachaya lords (3, 6, 10, 11) improve with time
        elif nature == "Upachaya":
            positive_effects.append(f"{planet.title()} as lord of {house}th house brings gradual growth in: {', '.join(areas)}")

        # Dusthana lords (6, 8, 12) can be challenging
        elif nature == "Dusthana":
            negative_effects.append(f"{planet.title()} as lord of {house}th house may bring challenges in: {', '.join(areas)}")

    return {"positive": positive_effects, "negative": negative_effects}


def interpret_house_placement(planet: str, house_placed: int) -> dict[str, str | list[str]]:
    """Interpret effects of planet placed in a specific house.

    Args:
        planet: Planet name
        house_placed: House number where planet is placed

    Returns:
        Dictionary with placement effects

    """
    house_info = HOUSE_SIGNIFICATIONS.get(house_placed, {})
    areas = house_info.get("areas", [])
    nature = house_info.get("nature", "")

    return {
        "description": f"{planet.title()} placed in {house_placed}th house focuses dasha on: {', '.join(areas)}",
        "areas_activated": areas,
        "house_nature": nature,
    }


def calculate_dasha_strength(
    houses_owned: list[int],
    house_placed: int,
    dignity: DignityStatus,
) -> PredictionStrength:
    """Calculate overall strength of dasha period effects.

    Args:
        houses_owned: Houses the planet rules
        house_placed: House where planet is placed
        dignity: Planetary dignity status

    Returns:
        PredictionStrength enum value

    """
    good_houses = [HOUSE_1_SELF, HOUSE_4_HOME, HOUSE_5_CHILDREN, HOUSE_7_MARRIAGE, HOUSE_9_FORTUNE, HOUSE_10_CAREER, HOUSE_11_GAINS]

    strength_score = _calculate_lordship_score(houses_owned, good_houses)
    strength_score += _calculate_placement_score(house_placed, good_houses)
    strength_score += _calculate_dignity_score(dignity)

    return _classify_dasha_strength(strength_score)


def _calculate_lordship_score(houses_owned: list[int], good_houses: list[int]) -> int:
    """Calculate strength score from house lordship."""
    return sum(2 for house in houses_owned if house in good_houses)


def _calculate_placement_score(house_placed: int, good_houses: list[int]) -> int:
    """Calculate strength score from house placement."""
    return 2 if house_placed in good_houses else 0


def _calculate_dignity_score(dignity: DignityStatus) -> int:
    """Calculate strength score from planetary dignity."""
    score = 0
    if dignity.is_exalted:
        score += 3
    elif dignity.is_debilitated:
        score -= 3
    if dignity.is_retrograde:
        score += 1
    return score


def _classify_dasha_strength(strength_score: int) -> PredictionStrength:
    """Classify strength score into PredictionStrength enum."""
    if strength_score >= STRENGTH_VERY_STRONG_THRESHOLD:
        return PredictionStrength.VERY_STRONG
    if strength_score >= STRENGTH_STRONG_THRESHOLD:
        return PredictionStrength.STRONG
    if strength_score >= STRENGTH_MODERATE_THRESHOLD:
        return PredictionStrength.MODERATE
    if strength_score >= STRENGTH_WEAK_THRESHOLD:
        return PredictionStrength.WEAK
    return PredictionStrength.VERY_WEAK


def generate_life_area_predictions(planet: str, houses_owned: list[int], house_placed: int) -> dict[str, str]:
    """Generate predictions for different life areas during dasha.

    Args:
        planet: Planet name
        houses_owned: Houses the planet rules
        house_placed: House where planet is placed

    Returns:
        Dictionary mapping life areas to specific predictions

    """
    planet_data = PLANET_SIGNIFICATIONS.get(planet, {})

    return {
        LifeArea.CAREER: _predict_career(planet, houses_owned, house_placed, planet_data),
        LifeArea.FINANCE: _predict_finance(houses_owned, house_placed),
        LifeArea.RELATIONSHIPS: _predict_relationships(planet, houses_owned, house_placed),
        LifeArea.HEALTH: _predict_health(houses_owned, house_placed, planet_data),
        LifeArea.EDUCATION: _predict_education(planet, houses_owned, house_placed),
        LifeArea.SPIRITUALITY: _predict_spirituality(planet, houses_owned, house_placed),
        LifeArea.FAMILY: _predict_family(planet, houses_owned, house_placed),
        LifeArea.TRAVEL: _predict_travel(houses_owned, house_placed),
    }


def _predict_career(planet: str, houses_owned: list[int], house_placed: int, planet_data: dict) -> str:
    """Generate career prediction."""
    if HOUSE_10_CAREER in houses_owned or house_placed == HOUSE_10_CAREER:
        career_domains = planet_data.get("career_domains", [])
        return f"Strong career period. Focus on: {', '.join(career_domains[:3])}. Recognition and advancement likely."
    if HOUSE_6_ENEMIES in houses_owned or house_placed == HOUSE_6_ENEMIES:
        return "Competitive work environment. Service-oriented work favored. Overcome obstacles through effort."
    return f"Career influenced by {planet}'s natural significations. Moderate progress expected."


def _predict_finance(houses_owned: list[int], house_placed: int) -> str:
    """Generate finance prediction."""
    if HOUSE_2_WEALTH in houses_owned or house_placed in (HOUSE_2_WEALTH, HOUSE_11_GAINS) or HOUSE_11_GAINS in houses_owned:
        return "Good period for wealth accumulation. Focus on savings and investments."
    if HOUSE_8_TRANSFORMATION in houses_owned or house_placed == HOUSE_8_TRANSFORMATION:
        return "Unexpected gains possible through inheritance or joint resources. Financial transformations. Manage debts carefully."
    return "Financial stability requires effort. Avoid major risks."


def _predict_relationships(planet: str, houses_owned: list[int], house_placed: int) -> str:
    """Generate relationships prediction."""
    if HOUSE_7_MARRIAGE in houses_owned or house_placed == HOUSE_7_MARRIAGE:
        return "Important period for partnerships and marriage. New relationships or strengthening of existing bonds."
    if HOUSE_5_CHILDREN in houses_owned or house_placed == HOUSE_5_CHILDREN:
        return "Romance and creative connections favored. Good for dating and socializing."
    if planet == "venus":
        return "Natural benefic for relationships. Harmony in personal life."
    return "Relationships require attention and effort. Communication is key."


def _predict_health(houses_owned: list[int], house_placed: int, planet_data: dict) -> str:
    """Generate health prediction."""
    health_areas = planet_data.get("health_areas", [])
    if HOUSE_1_SELF in houses_owned or house_placed == HOUSE_1_SELF:
        return f"Focus on overall vitality. Pay attention to: {', '.join(health_areas[:2])}. Good period for health improvements."
    if HOUSE_6_ENEMIES in houses_owned or house_placed == HOUSE_6_ENEMIES:
        return f"Monitor health carefully. Areas to watch: {', '.join(health_areas[:2])}. Regular check-ups advised."
    return f"Moderate health period. Be mindful of: {', '.join(health_areas[:2])}."


def _predict_education(planet: str, houses_owned: list[int], house_placed: int) -> str:
    """Generate education prediction."""
    if HOUSE_4_HOME in houses_owned or house_placed in (HOUSE_4_HOME, HOUSE_5_CHILDREN) or HOUSE_5_CHILDREN in houses_owned:
        return "Excellent period for learning and education. Intellectual pursuits favored."
    if HOUSE_9_FORTUNE in houses_owned or house_placed == HOUSE_9_FORTUNE:
        return "Higher education and advanced learning supported. Good for research and philosophy."
    if planet in {"mercury", "jupiter"}:
        return "Natural support for educational pursuits. Learning comes easily."
    return "Learning possible but requires focused effort."


def _predict_spirituality(planet: str, houses_owned: list[int], house_placed: int) -> str:
    """Generate spirituality prediction."""
    if HOUSE_9_FORTUNE in houses_owned or house_placed in (HOUSE_9_FORTUNE, HOUSE_12_LOSS) or HOUSE_12_LOSS in houses_owned:
        return "Strong spiritual growth period. Dharma and higher purpose emphasized."
    if planet in {"jupiter", "kethu"}:
        return "Natural inclination toward spirituality. Meditation and inner work beneficial."
    return "Spiritual development through daily practice and mindfulness."


def _predict_family(planet: str, houses_owned: list[int], house_placed: int) -> str:
    """Generate family prediction."""
    if HOUSE_2_WEALTH in houses_owned or house_placed in (HOUSE_2_WEALTH, HOUSE_4_HOME) or HOUSE_4_HOME in houses_owned:
        return "Important focus on family matters. Strengthening family bonds. Property matters active."
    if planet == "moon":
        return "Emotional connection with family strong. Mother's influence prominent."
    return "Family life stable. Normal interactions and support."


def _predict_travel(houses_owned: list[int], house_placed: int) -> str:
    """Generate travel prediction."""
    if HOUSE_3_SIBLINGS in houses_owned or house_placed == HOUSE_3_SIBLINGS:
        return "Short trips and local travel frequent. Good for communication and nearby connections."
    if HOUSE_9_FORTUNE in houses_owned or house_placed in (HOUSE_9_FORTUNE, HOUSE_12_LOSS) or HOUSE_12_LOSS in houses_owned:
        return "Long-distance travel likely. Foreign connections possible. Pilgrimage favored."
    return "Moderate travel. Plan trips during favorable sub-periods."


def generate_recommendations(planet: str, houses_owned: list[int]) -> dict[str, list[str]]:
    """Generate actionable recommendations for dasha period.

    Args:
        planet: Planet name
        houses_owned: Houses the planet rules

    Returns:
        Dictionary with recommended actions, things to avoid, favorable activities

    """
    # General recommendations based on planet
    recommendations = {
        "sun": {
            "do": ["Lead projects", "Seek recognition", "Work with government", "Focus on health", "Build confidence"],
            "avoid": ["Ego conflicts", "Overwork", "Ignoring health", "Power struggles"],
            "favorable": ["Government work", "Leadership roles", "Medical checkups", "Spiritual practices"],
        },
        "moon": {
            "do": ["Nurture emotions", "Connect with public", "Travel", "Spend time with mother", "Practice mindfulness"],
            "avoid": ["Emotional decisions", "Overthinking", "Isolation", "Irregular routines"],
            "favorable": ["Public relations", "Hospitality work", "Travel", "Water activities", "Family time"],
        },
        "mars": {
            "do": ["Take initiative", "Exercise regularly", "Deal with property matters", "Be courageous", "channeled action"],
            "avoid": ["Aggression", "Impulsive decisions", "Conflicts", "Risky ventures", "Accidents"],
            "favorable": ["Sports", "Engineering projects", "Property deals", "Competitive activities"],
        },
        "mercury": {
            "do": ["Communicate clearly", "Start business", "Study and learn", "Network", "Write and teach"],
            "avoid": ["Mental stress", "Overthinking", "Dishonesty", "Scattered focus"],
            "favorable": ["Business ventures", "Education", "Writing", "Teaching", "Commerce"],
        },
        "jupiter": {
            "do": ["Expand knowledge", "Be generous", "Teach others", "Spiritual practices", "Financial planning"],
            "avoid": ["Over-optimism", "Excess", "Complacency", "Ignoring details"],
            "favorable": ["Teaching", "Religious activities", "Higher education", "Financial growth", "Children's matters"],
        },
        "venus": {
            "do": ["Enjoy relationships", "Pursue arts", "Invest in comfort", "Marriage matters", "Creative work"],
            "avoid": ["Over-indulgence", "Laziness", "Excess spending", "Superficiality"],
            "favorable": ["Arts and culture", "Marriage", "Luxury purchases", "Entertainment", "Beauty treatments"],
        },
        "saturn": {
            "do": ["Work hard", "Be disciplined", "Serve others", "Practice patience", "Long-term planning"],
            "avoid": ["Laziness", "Depression", "Shortcuts", "Ignoring responsibilities"],
            "favorable": ["Hard work", "Service", "Discipline", "Structure", "Long-term investments"],
        },
        "rahu": {
            "do": ["Embrace innovation", "Foreign connections", "Research work", "Think unconventionally", "Technology"],
            "avoid": ["Deception", "Addictions", "Unethical shortcuts", "Obsessions"],
            "favorable": ["Technology", "Foreign ventures", "Research", "Unconventional paths", "Innovation"],
        },
        "kethu": {
            "do": ["Spiritual practices", "Detachment", "Occult studies", "Inner work", "Let go of past"],
            "avoid": ["Isolation", "Confusion", "Material obsession", "Ignoring health"],
            "favorable": ["Meditation", "Spiritual retreat", "Occult studies", "Technical research", "Solitude"],
        },
    }

    base_rec = recommendations.get(planet, {"do": [], "avoid": [], "favorable": []})

    # Add house-specific recommendations
    if HOUSE_10_CAREER in houses_owned:
        base_rec["do"].append("Focus on career advancement")
        base_rec["favorable"].append("Professional initiatives")

    if HOUSE_7_MARRIAGE in houses_owned:
        base_rec["do"].append("Nurture partnerships")
        base_rec["favorable"].append("Marriage and business partnerships")

    if HOUSE_6_ENEMIES in houses_owned or HOUSE_8_TRANSFORMATION in houses_owned or HOUSE_12_LOSS in houses_owned:
        base_rec["do"].append("Address challenges proactively")
        base_rec["avoid"].append("Major risks in this house's matters")

    return {
        "recommended_actions": base_rec["do"],
        "things_to_avoid": base_rec["avoid"],
        "favorable_activities": base_rec["favorable"],
    }


def analyze_bhukti_combination(maha_lord: str, bhukti_lord: str) -> BhuktiPrediction:
    """Analyze combined effects of Mahadasha and Bhukti lords.

    Args:
        maha_lord: Mahadasha planet
        bhukti_lord: Bhukti (sub-period) planet

    Returns:
        BhuktiPrediction with combined analysis

    """
    # Define planetary relationships for harmony
    friendly_planets = {
        "sun": ["moon", "mars", "jupiter"],
        "moon": ["sun", "mercury"],
        "mars": ["sun", "moon", "jupiter"],
        "mercury": ["sun", "venus"],
        "jupiter": ["sun", "moon", "mars"],
        "venus": ["mercury", "saturn"],
        "saturn": ["mercury", "venus"],
        "rahu": ["saturn", "mercury", "venus"],
        "kethu": ["mars", "jupiter"],
    }

    enemy_planets = {
        "sun": ["venus", "saturn"],
        "moon": ["none"],
        "mars": ["mercury"],
        "mercury": ["moon"],
        "jupiter": ["mercury", "venus"],
        "venus": ["sun", "moon"],
        "saturn": ["sun", "moon", "mars"],
        "rahu": ["sun", "moon"],
        "kethu": ["sun", "moon"],
    }

    # Determine harmony level
    harmony = "Neutral"
    if maha_lord == bhukti_lord:
        harmony = "Excellent"
        combined_theme = f"Pure {maha_lord.title()} influence. Intensified natural significations."
    elif bhukti_lord in friendly_planets.get(maha_lord, []):
        harmony = "Good"
        combined_theme = f"{maha_lord.title()} and {bhukti_lord.title()} work harmoniously together."
    elif bhukti_lord in enemy_planets.get(maha_lord, []):
        harmony = "Challenging"
        combined_theme = f"Conflicting energies between {maha_lord.title()} and {bhukti_lord.title()}."
    else:
        harmony = "Neutral"
        combined_theme = f"{maha_lord.title()} main theme with {bhukti_lord.title()} sub-influences."

    # Generate specific predictions
    maha_data = PLANET_SIGNIFICATIONS.get(maha_lord, {})
    bhukti_data = PLANET_SIGNIFICATIONS.get(bhukti_lord, {})

    maha_positive = maha_data.get("positive_traits", [])
    bhukti_positive = bhukti_data.get("positive_traits", [])

    specific_predictions = [
        f"Main theme: {maha_positive[0] if maha_positive else 'General growth'} from {maha_lord.title()}",
        f"Sub-theme: {bhukti_positive[0] if bhukti_positive else 'Supporting influences'} from {bhukti_lord.title()}",
    ]

    # Determine dominant planet
    # Generally Mahadasha lord is more dominant
    dominant = maha_lord
    if harmony == "Excellent":
        dominant = maha_lord  # Same planet, fully dominant
    elif harmony == "Challenging":
        # Bhukti can disrupt if enemy
        specific_predictions.append(f"{bhukti_lord.title()}'s influence may create obstacles to {maha_lord.title()}'s goals")

    # Optimal activities combine both planets
    maha_activities = maha_data.get("career_domains", [])
    bhukti_activities = bhukti_data.get("career_domains", [])
    optimal = list(set(maha_activities[:2] + bhukti_activities[:2]))

    # Cautions
    maha_negative = maha_data.get("negative_traits", [])
    bhukti_negative = bhukti_data.get("negative_traits", [])
    cautions = list(set(maha_negative[:2] + bhukti_negative[:2]))

    return BhuktiPrediction(
        maha_lord=maha_lord,
        bhukti_lord=bhukti_lord,
        combined_theme=combined_theme,
        harmony_level=harmony,
        dominant_planet=dominant,
        specific_predictions=specific_predictions,
        optimal_activities=optimal,
        cautions=cautions,
    )


def generate_comprehensive_dasha_prediction(context: DashaContext) -> DashaPrediction:
    """Generate comprehensive prediction for a dasha period.

    Args:
        context: DashaContext with all prediction parameters

    Returns:
        Complete DashaPrediction object

    """
    planet_data = get_planet_natural_effects(context.planet)

    dignity = DignityStatus(
        is_exalted=context.is_exalted,
        is_debilitated=context.is_debilitated,
        is_retrograde=context.is_retrograde,
    )

    theme_modifier = _determine_theme_modifier(dignity)

    significations = planet_data.get("natural_significations", ["general life"])[:3]
    general_theme = f"{context.planet.title()} {context.dasha_level}: {theme_modifier}. Focus on {significations}"

    lordship_effects = interpret_house_lordship(context.planet, context.houses_owned)

    strength = calculate_dasha_strength(context.houses_owned, context.house_placed, dignity)

    life_predictions = generate_life_area_predictions(context.planet, context.houses_owned, context.house_placed)

    recs = generate_recommendations(context.planet, context.houses_owned)
    timing_map = _determine_event_timing(context.planet)

    return DashaPrediction(
        dasha_lord=context.planet,
        dasha_level=context.dasha_level,
        general_theme=general_theme,
        positive_effects=planet_data.get("positive_traits", []) + lordship_effects["positive"],
        negative_effects=planet_data.get("negative_traits", []) + lordship_effects["negative"],
        life_area_predictions=life_predictions,
        recommended_actions=recs["recommended_actions"],
        things_to_avoid=recs["things_to_avoid"],
        favorable_activities=recs["favorable_activities"],
        strength=strength,
        key_events_timing=timing_map,
    )


def _determine_theme_modifier(dignity: DignityStatus) -> str:
    """Determine theme modifier based on planetary dignity."""
    if dignity.is_exalted:
        return "Highly favorable period with strong positive results"
    if dignity.is_debilitated:
        return "Challenging period requiring extra effort"
    if dignity.is_retrograde:
        return "Intensified effects with focus on past matters"
    return "Natural expression of planet's significations"


def _determine_event_timing(planet: str) -> dict[str, EventTiming]:
    """Determine event timing based on planet nature."""
    fast_planets = {"moon", "mercury", "sun"}
    slow_planets = {"saturn", "jupiter", "rahu", "kethu"}

    if planet in fast_planets:
        return {
            "Initial results": EventTiming.EARLY,
            "Peak effects": EventTiming.MIDDLE,
        }
    if planet in slow_planets:
        return {
            "Gradual buildup": EventTiming.EARLY,
            "Peak effects": EventTiming.LATE,
        }
    return {"Active throughout": EventTiming.THROUGHOUT}
