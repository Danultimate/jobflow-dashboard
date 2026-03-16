from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "job-dashboard-api"
    env: str = "development"
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/job_dashboard"
    redis_url: str = "redis://localhost:6379/0"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    enable_automation: bool = False
    allowed_origins: str = "http://localhost:3000,http://localhost"
    auth_username: str = "admin"
    auth_password: str = "change-me"
    jwt_secret: str = "change-this-secret"
    jwt_expire_minutes: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()
