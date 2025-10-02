# from fastapi import APIRouter
# from pydantic import BaseModel
# from app.services import analysis_service

# router = APIRouter(prefix="/analyses", tags=["Analyses"])

# class AnalysisCreate(BaseModel):
#     organization_id: str

# @router.post("/")
# async def create_analysis(data: AnalysisCreate):
#     return await analysis_service.create(data.organization_id)

# @router.get("/{analysis_id}")
# async def get_analysis(analysis_id: str):
#     return await analysis_service.get(analysis_id)

# @router.get("/")
# async def list_analyses():
#     return await analysis_service.list_all()

# @router.put("/{analysis_id}/status")
# async def update_status(analysis_id: str, status: str):
#     return await analysis_service.update_status(analysis_id, status)
