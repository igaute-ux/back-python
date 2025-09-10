from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_analyses():
    return {"message": "Get analyses - TODO"}

@router.post("/request")
async def request_analysis():
    return {"message": "Request analysis - TODO"}