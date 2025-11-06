from fastapi import APIRouter
from app.api.routes import esg

api_router = APIRouter()

api_router.include_router(esg.router, prefix="/esg", tags=["esg"])