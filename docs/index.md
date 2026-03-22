# ndastro-api

**API to serve data for ndastro-ui** — a FastAPI-based backend providing Vedic astrology data and calculations.

## Features

- **Planetary positions** — sidereal planet positions using the Lahiri ayanamsa
- **Chart generation** — South Indian chart SVG output
- **Nakshatra & Panchanga** — nakshatra traits, panchanga elements, timing windows
- **Dasha systems** — Vimsottari dasha periods and predictions
- **Yogas** — Classical and extended planetary yoga detection
- **Ashtakavarga** — Sarva and Bhinna ashtakavarga calculations with transit predictions
- **Avasthas** — Age, alertness, mood and activity avastha analysis
- **Longevity** — Maraka, Rudra Trishoola and Maheswara analysis
- **Muhurta** — Durmuhurta, Varjyam, and Amrita Kala windows
- **Shadbala & Vimshopaka** — Planetary strength calculations
- **Multilingual** — Full i18n support via Babel/FastAPI-Babel

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| ORM | SQLModel + Alembic |
| Astro Engine | ndastro-engine |
| Ephemeris | Skyfield |
| Auth | PyJWT + Passlib |
| i18n | Babel + FastAPI-Babel |
| Testing | pytest + pytest-cov |
| Docs | MkDocs Material |
