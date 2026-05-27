"""API v1 routing module.

This module defines and includes all API v1 routers for authentication, user management, and astro endpoints.
"""

from fastapi import APIRouter

from ndastro_api.api.v1.ashtakavarga import router as ashtakavarga
from ndastro_api.api.v1.astro import router as astro
from ndastro_api.api.v1.avasthas import router as avasthas
from ndastro_api.api.v1.config import router as config
from ndastro_api.api.v1.dasha import router as dasha
from ndastro_api.api.v1.divisional import router as divisional
from ndastro_api.api.v1.health import router as health
from ndastro_api.api.v1.login import router as login
from ndastro_api.api.v1.logout import router as logout
from ndastro_api.api.v1.longevity import router as longevity
from ndastro_api.api.v1.muhurta import router as muhurta
from ndastro_api.api.v1.nakshatra import router as nakshatra
from ndastro_api.api.v1.strengths import router as strengths
from ndastro_api.api.v1.tiers import router as tier
from ndastro_api.api.v1.transits import router as transits
from ndastro_api.api.v1.upagrahas import router as upagrahas
from ndastro_api.api.v1.users import router as user
from ndastro_api.api.v1.yogas import router as yogas

router = APIRouter(prefix="/v1")
router.include_router(config)
router.include_router(login)
router.include_router(logout)
router.include_router(tier)
router.include_router(user)
router.include_router(astro)
router.include_router(health)
router.include_router(nakshatra)
router.include_router(yogas)
router.include_router(ashtakavarga)
router.include_router(dasha)
router.include_router(avasthas)
router.include_router(strengths)
router.include_router(transits)
router.include_router(longevity)
router.include_router(muhurta)
router.include_router(divisional)
router.include_router(upagrahas)
