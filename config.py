from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_REFRESH_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    DB_TEST_ENGINE: str
    DB_TEST_USERNAME: str
    DB_TEST_PASSWORD: str
    DB_TEST_HOST: str
    DB_TEST_PORT: str
    DB_TEST_DATABASE: str
    DB_STAGING_ENGINE: str
    DB_STAGING_USERNAME: str
    DB_STAGING_PASSWORD: str
    DB_STAGING_HOST: str
    DB_STAGING_PORT: str
    DB_STAGING_DATABASE: str
    DB_PRODUCTION_ENGINE: str
    DB_PRODUCTION_USERNAME: str
    DB_PRODUCTION_PASSWORD: str
    DB_PRODUCTION_HOST: str
    DB_PRODUCTION_PORT: str
    DB_PRODUCTION_DATABASE: str
    AWS_IPV4_PUBLIC_ADDRESS: str
    WEB_ENVIRONMENT: str
    OPENAI_API_KEY: str
    OPENAI_BOT_MODEL: str
    ADYEN_API_KEY: str
    ADYEN_MERCHANT_ACCOUNT: str
    ADYEN_CLIENT_KEY: str
    ADYEN_HMAC_KEY: str

    class Config:
        env_file = Path(Path(__file__).resolve().parent) / ".env"
        print(f"environment created - {Path(Path(__file__).resolve().name)}")

setting = Settings()