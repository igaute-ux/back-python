from fastapi import FastAPI
from app.api.router import api_router
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Adaptia API")
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Adaptia API"}