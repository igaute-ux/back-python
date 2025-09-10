from fastapi import APIRouter
from app.models.chat import ChatRequest
from app.services.langchain.workflows import run_prompt_1

router = APIRouter()

@router.post("/analyze-context")
async def analyze_context(data: ChatRequest):
    result = await run_prompt_1(
        organization_name=data.organization_name,
        country=data.country,
        website=data.website
    )
    return {"analysis": result}