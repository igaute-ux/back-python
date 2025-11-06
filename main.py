from fastapi import FastAPI
from app.api.router import api_router
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Adaptia API")
app.include_router(api_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # o ["http://localhost:3000"] si querés restringir
    allow_credentials=True,
    allow_methods=["*"],   # 👈 acepta OPTIONS, POST, GET, etc
    allow_headers=["*"],   # 👈 acepta cualquier header
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Adaptia API"}