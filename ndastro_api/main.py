"""Main entry point for the ndastro_api application.

This module sets up the FastAPI application, including admin interface initialization and routing.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ndastro_api.api.router import router
from ndastro_api.core.config import settings
from ndastro_api.core.exceptions.http_exceptions import CustomAPIException
from ndastro_api.core.setup import create_application, lifespan_factory
from ndastro_api.core.utils.data_loader import astro_data


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Return a custom lifespan that includes admin initialization and data preloading."""
    # Get the default lifespan
    default_lifespan = lifespan_factory()

    # Run the default lifespan initialization and our admin initialization
    async with default_lifespan(app):
        # Preload all astrological data on startup for better performance
        astro_data.preload_all()
        yield


app = create_application(router=router, settings=settings, lifespan=lifespan)

logger = logging.getLogger(__name__)


@app.exception_handler(CustomAPIException)
async def app_exception_handler(_request: Request, exc: CustomAPIException) -> JSONResponse:
    """Handle CustomAPIException by logging the error and returning a JSON response."""
    logger.error("Application error: %s", exc.message)
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})
