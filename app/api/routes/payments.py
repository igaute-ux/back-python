# from fastapi import APIRouter
# from app.services import payment_service

# router = APIRouter(prefix="/payments", tags=["Payments"])

# @router.post("/{analysis_id}")
# async def create_payment(analysis_id: str, user_id: str):
#     return await payment_service.create(analysis_id, user_id)

# @router.get("/{payment_id}")
# async def get_payment(payment_id: str):
#     return await payment_service.get(payment_id)