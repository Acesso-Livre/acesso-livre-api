import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    api: str
    fronturl: str
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    reset_token_expire_minutes: int
    bucket_name: str
    bucket_endpoint_url: str
    bucket_secret_key: str
    mode: str = "prod"
    # EmailJS Configuration
    emailjs_service_id: str
    emailjs_template_id: str
    emailjs_public_key: str  # Public Key (user_id)
    emailjs_private_key: str  # Private Key (accessToken)


settings = Settings()

if settings.mode == "development":
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    print("-----SQLAlchemy debug logs ativados (modo dev)-----")
