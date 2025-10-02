from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    
    # Supabase
    DATABASE_URL: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()