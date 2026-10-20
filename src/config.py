from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

    BASE_URL: str = "http://localhost:8000"
    API_V1_PREFIX: str = "/api/v1"

    DB_FILE_NAME: str = "db.sqlite3"

    ACTIVATION_TOKEN_TTL_HOURS: int = 24

    PATH_TO_EMAIL_TEMPLATES_DIR: Path = SRC_DIR / "notifications" / "templates"
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 1025
    EMAIL_HOST_USER: str = "testuser"
    EMAIL_HOST_PASSWORD: str = "test_password"
    EMAIL_USE_TLS: bool = False

    @property
    def DB_URI(self) -> str:
        return f"sqlite+aiosqlite:///{BASE_DIR / self.DB_FILE_NAME}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
