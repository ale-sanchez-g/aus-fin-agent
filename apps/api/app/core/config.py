from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    CDR_BASE_URL: str = "https://api.cdr.gov.au"
    CDR_MOCK_MODE: bool = True
    AWS_REGION: str = "ap-southeast-2"
    AWS_BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""
    COGNITO_REGION: str = "ap-southeast-2"
    S3_REPORTS_BUCKET: str = "aus-fin-agent-reports-dev"
    ENVIRONMENT: str = "dev"
    FEATURE_FLAG_CONSENTED_DATA_MODE: bool = False
    FEATURE_FLAG_LLM_RERANK: bool = False
    FEATURE_FLAG_MCP_DETAIL_ENRICH: bool = False
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "dev-secret-key"
    DISCLAIMER_TEXT: str = (
        "This report is for discovery purposes only and does not constitute "
        "personal financial advice. Always consult a licensed financial adviser."
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
