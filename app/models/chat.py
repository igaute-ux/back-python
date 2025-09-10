from pydantic import BaseModel

class ChatRequest(BaseModel):
    organization_name: str
    country: str
    website: str
