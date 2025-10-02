# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from app.services.auth_service import authenticate_user, create_access_token, register_user

# router = APIRouter(prefix="/auth", tags=["Auth"])

# class UserRegister(BaseModel):
#     name: str
#     surname: str
#     email: str
#     password: str

# class UserLogin(BaseModel):
#     email: str
#     password: str

# @router.post("/register")
# async def register(data: UserRegister):
#     return await register_user(data)

# @router.post("/login")
# async def login(data: UserLogin):
#     user = await authenticate_user(data.email, data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     token = create_access_token({"sub": user.id})
#     return {"access_token": token, "token_type": "bearer"}
