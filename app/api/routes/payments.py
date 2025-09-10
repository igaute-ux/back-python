from fastapi import APIRouter

router = APIRouter()

@router.post("/create")
async def create_payment():
    return {"message": "Create payment - TODO"}

@router.get("/{payment_id}")
async def get_payment():
    return {"message": "Get payment - TODO"}