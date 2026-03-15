"""Global configuration via pydantic-settings. Single source of truth for all env vars."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "ai-sdr"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    API_KEY: str = ""  # For API authentication

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ai_sdr:ai_sdr@localhost:5432/ai_sdr"
    DB_POOL_SIZE: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM (via LiteLLM)
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL_FAST: str = "claude-haiku-4-5-20251001"
    LLM_MODEL_MID: str = "claude-sonnet-4-6"
    LLM_API_KEY: str = ""
    LLM_MAX_TOKENS: int = 4096
    LLM_TEMPERATURE: float = 0.3

    # Email
    EMAIL_PROVIDER: str = "resend"  # "resend"
    RESEND_API_KEY: str = ""
    EMAIL_FROM_ADDRESS: str = ""
    EMAIL_FROM_NAME: str = ""

    # Calendar
    CALCOM_API_KEY: str = ""
    CALCOM_BASE_URL: str = "https://api.cal.com/v2"

    # CRM - Salesforce
    SALESFORCE_USERNAME: str = ""
    SALESFORCE_PASSWORD: str = ""
    SALESFORCE_SECURITY_TOKEN: str = ""
    SALESFORCE_DOMAIN: str = "login"  # "login" for production, "test" for sandbox

    # Slack
    SLACK_WEBHOOK_URL: str = ""

    # Web Scraping
    SCRAPER_USER_AGENT: str = "AI-SDR-Bot/0.1"
    SCRAPER_RATE_LIMIT_SECONDS: float = 2.0
    DUCKDUCKGO_MAX_RESULTS: int = 10


settings = Settings()
