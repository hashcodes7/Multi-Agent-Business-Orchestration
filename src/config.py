import os
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings powered by Pydantic.
    Reads from OS environment variables first, then falls back to local .env files.
    """
    # Environment
    APP_ENV: Literal["dev", "staging", "prod", "test"] = "dev"

    # External APIs
    ECOMMERCE_API_BASE_URL: str = "https://fakestoreapi.com"

    # Server Configuration (for local runner / dev defaults)
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        # Precedence: OS env vars > .env.<APP_ENV> > .env
        env_file=(
            f".env.{os.getenv('APP_ENV', 'dev')}",
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Dependency injection provider returning a cached Settings singleton.
    Can be overridden in tests using app.dependency_overrides[get_settings].
    """
    return Settings()
