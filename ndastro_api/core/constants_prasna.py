"""Prasna-specific application constants.

These are the Prasna query-topic descriptions keyed by house (HouseCode →
Houses enum).  They encode the empathetic 'you came to ask about…' framing
used when generating a reading paragraph — distinct from the classical
shastra rules in constants_vedic.py.

Each entry is a 3-tuple:
  (short_label, single_phrase, detailed_paragraph)
"""

from __future__ import annotations

from ndastro_engine.enums import HouseCode, Houses  # noqa: F401  (HouseCode re-exported for callers)

HOUSE_TOPICS: dict[Houses, tuple[str, str, str]] = {
    Houses.HOUSE1: (
        "Health & Self",
        "your own health, body, or a deeply personal matter",
        "You appear to carry a concern about yourself — perhaps your health, your appearance,"
        " your vitality, or something very personal that you have not yet shared with others.",
    ),
    Houses.HOUSE2: (
        "Wealth & Family",
        "a financial matter, money, family, or an asset",
        "The indicators suggest a question about money — savings, income, a pending payment,"
        " an asset you hold, or a family financial matter that weighs on you.",
    ),
    Houses.HOUSE3: (
        "Communication & Siblings",
        "a sibling, a short journey, an agreement, or a decision requiring courage",
        "The chart points toward a matter involving a brother, sister, or close neighbour;"
        " or it may be about a short trip, a message, a document, or summoning the courage"
        " to make a decision.",
    ),
    Houses.HOUSE4: (
        "Home, Property & Mother",
        "property, your home, a vehicle, your mother, or an educational institution",
        "You seem to have come with a question about land, a house, a vehicle, a domestic"
        " matter, or your relationship with your mother or your roots.",
    ),
    Houses.HOUSE5: (
        "Children & Creativity",
        "children, a romantic relationship, a creative project, or an investment",
        "The indicators point to something involving a child, a love affair, a creative"
        " endeavour, or a speculative investment — something you hold close to your heart.",
    ),
    Houses.HOUSE6: (
        "Enemies, Debt & Disease",
        "a health problem, a debt, an enemy or rival, or a legal dispute",
        "There is a sense of conflict or difficulty — you may be asking about an illness,"
        " a recurring problem, a debt you need to clear, a rivalry, or a pending legal matter.",
    ),
    Houses.HOUSE7: (
        "Marriage & Partnership",
        "a relationship — marriage, a business partner, or an agreement with another",
        "The strongest indication is a question about another person — a spouse, a life"
        " partner, a business associate, or a significant agreement or negotiation involving"
        " someone else.",
    ),
    Houses.HOUSE8: (
        "Crisis, Secrets & Transformation",
        "an inheritance, a sudden event, a transformation, or a hidden matter",
        "You appear to carry something heavy — an urgent or hidden concern, perhaps about"
        " an inheritance, a sudden crisis, a major life change, or information that has not"
        " yet come to light.",
    ),
    Houses.HOUSE9: (
        "Fortune, Dharma & Long Journeys",
        "luck, religion, a long journey, your father, or seeking guidance on the right path",
        "The chart suggests a quest for meaning or direction — you may be asking about"
        " fortune, a long journey, a religious or spiritual matter, your father, or simply"
        " what the right path forward looks like.",
    ),
    Houses.HOUSE10: (
        "Career & Status",
        "your career, a job matter, a promotion, or dealings with authority",
        "All indicators converge on professional life — your career, a job situation,"
        " recognition you are seeking, or a matter involving an employer, government, or"
        " authority figure.",
    ),
    Houses.HOUSE11: (
        "Gains & Desires",
        "income, a pending gain, the fulfilment of a wish, or a friendship",
        "You carry hope with you — perhaps a pending payment, a wish you want to see"
        " fulfilled, a gain you are waiting for, or something about a friend or a network"
        " connection.",
    ),
    Houses.HOUSE12: (
        "Loss, Foreign & Spiritual",
        "a large expense, a loss, foreign travel, hospitalisation, or a spiritual question",
        "The indicators suggest a matter of endings or release — an expense, a loss, going"
        " abroad, hospitalisation or isolation, or a deep spiritual question.",
    ),
}
