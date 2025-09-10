from fastapi import APIRouter
from app.api.routes import auth, companies, analyses, payments, esg

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(esg.router, prefix="/esg", tags=["esg"])