from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    organization_name: str
    country: str
    website: str
