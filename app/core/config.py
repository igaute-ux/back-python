from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    ENVIRONMENT: str = "development"
    
    DATABASE_URL: str = ""

    OPENAI_API_KEY: str = ""

    SUPABASE_URL: str = ""

    SUPABASE_ANON_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()