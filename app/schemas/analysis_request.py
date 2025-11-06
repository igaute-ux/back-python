from pydantic import BaseModel
from uuid import UUID

class AnalysisRequest(BaseModel):
    organization_name: str
    country: str
    website: str