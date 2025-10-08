from fastapi import APIRouter
from app.api.routes import auth, organizations, analyses, payments, esg, users

api_router = APIRouter()

# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router)
api_router.include_router(organizations.router)
# api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
# api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(esg.router, prefix="/esg", tags=["esg"])