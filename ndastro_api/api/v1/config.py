"""Engine configuration endpoint.

GET  /v1/config  — returns the current ndastro-engine defaults (read-only).

Settings are resolved at startup from environment variables and can be
overridden per-request on calculation endpoints via query parameters.
Mutating the global config at runtime via HTTP is intentionally not supported;
see the individual calculation endpoints for per-request overrides.
"""

from __future__ import annotations

import ndastro_engine.config as engine_config
from fastapi import APIRouter
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies

router = APIRouter(prefix="/config", tags=["Config"], dependencies=get_conditional_dependencies())


class EngineConfigResponse(BaseModel):
    """Current ndastro-engine calculation settings."""

    position_reference: str
    node_type: str
    ayanamsa_delta: float
    dasa_year_length: float
    apply_nutation: bool
    apply_aberration: bool
    apply_grav_deflection: bool
    sunrise_definition: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "position_reference": "geocentric",
                "node_type": "true",
                "ayanamsa_delta": 0.0,
                "dasa_year_length": 365.25,
                "apply_nutation": True,
                "apply_aberration": True,
                "apply_grav_deflection": True,
                "sunrise_definition": "geometric",
            }
        }
    }


@router.get("", response_model=EngineConfigResponse, summary="Get current engine settings")
def get_engine_config() -> EngineConfigResponse:
    """Return the active ndastro-engine calculation settings.

    These are the server-wide defaults resolved from environment variables at
    startup.  Individual calculation endpoints accept query parameters that
    override these defaults **for that request only**, without affecting the
    global state.

    Useful for debugging: clients can verify which node type, position
    reference, and ayanamsa correction the server is using.
    """
    s = engine_config.settings
    return EngineConfigResponse(
        position_reference=s.position_reference,
        node_type=s.node_type,
        ayanamsa_delta=s.ayanamsa_delta,
        dasa_year_length=s.dasa_year_length,
        apply_nutation=s.apply_nutation,
        apply_aberration=s.apply_aberration,
        apply_grav_deflection=s.apply_grav_deflection,
        sunrise_definition=s.sunrise_definition,
    )
