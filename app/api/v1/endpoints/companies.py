from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_companies():
    return {"message": "Get companies - TODO"}

@router.post("/")
async def create_company():
    return {"message": "Create company - TODO"}