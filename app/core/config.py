from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    SECRET_KEY: str = "dev-secret-key"
    ENVIRONMENT: str = "development"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()