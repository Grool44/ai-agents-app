from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AI Agents Manager"
    DATABASE_URL: str = "sqlite:///./ai_agents.db"
    SECRET_KEY: str = "secret-key"
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]
    API_V1_PREFIX: str = "/api/v1"

settings = Settings()
