from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    secret_key: str
    refresh_secret_key: str
    algorithm: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    class Config:
        env_file = Path(Path(__file__).resolve().parent) / ".env"
        print(f"environment created - {Path(Path(__file__).resolve().name)}")

setting = Settings()