from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./worker.db"
    NODE_ADAPTER_URL: str = "http://node-adapter:4000"
    SYNC_INTERVAL_HOURS: int = 6
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "dev"
    AWS_REGION: str = "ap-southeast-2"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
