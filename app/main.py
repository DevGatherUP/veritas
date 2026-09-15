from fastapi import FastAPI
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(api_router, prefix="/api/v1")
