from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./worker.db"
    CDR_BASE_URL: str = "https://api.cdr.gov.au"
    CDR_MOCK_MODE: bool = True
    SYNC_INTERVAL_HOURS: int = 6
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "dev"
    AWS_REGION: str = "ap-southeast-2"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
