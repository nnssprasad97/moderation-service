# Configuration management using Pydantic BaseSettings for environment variables
from pydantic_settings import BaseSettings

# Settings class for application configuration loaded from environment
class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    RATE_LIMIT_REFILL_RATE: int = 5
    RATE_LIMIT_CAPACITY: int = 10
    QUEUE_NAME: str = "content_moderation_queue"

    class Config:
        env_file = ".env"

settings = Settings()
