import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    api: str
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    reset_token_expire_minutes: int
    bucket_name: str
    bucket_endpoint_url: str
    bucket_secret_key: str
    mode: str = "prod"


settings = Settings()

if settings.mode == "development":
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    print("-----SQLAlchemy debug logs ativados (modo dev)-----")
