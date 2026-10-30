import sys
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "dev"
    ECOMMERCE_API_BASE_URL: str = "https://fakestoreapi.com"
    model_config = SettingsConfigDict(extra="ignore")


def setenv() -> Settings:
    # Step 1: if -prod flag is passed
    if "-prod" in sys.argv:
        env_file = ".env.prod"

    # Step 2: Default to development environment
    else:
        env_file = ".env.dev"

    # Step 3: Load and return configuration
    settings = Settings(_env_file=env_file)
    return settings