from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class AnalysisRequest(BaseModel):
    organization_name: str
    country: str
    website: str
    industry: str
    document: Optional[str] = None



class IndustryRequest(BaseModel):
    industry: str