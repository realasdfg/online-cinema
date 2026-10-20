import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DB_FILE_NAME: str = "db.sqlite3"

    @property
    def DB_URI(self) -> str:
        return f"sqlite+aiosqlite:///{self.BASE_DIR / self.DB_FILE_NAME}"


@lru_cache
def get_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", "developing")
    if environment == "testing":
        pass
    return Settings()
