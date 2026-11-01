import os

from pydantic_settings import BaseSettings, SettingsConfigDict


APP_ENV = os.getenv("MABOP_ENV", "dev")
ENV_FILE = f".env.{APP_ENV}"


class Settings(BaseSettings):

    APP_ENV: str = APP_ENV
    ECOMMERCE_API_BASE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore"
    )

def setenv() -> Settings:
    return Settings()