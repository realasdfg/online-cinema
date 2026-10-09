from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    db_name: str = "db.sqlite3"

    @property
    def db_uri(self) -> str:
        return f"sqlite+aiosqlite:///{BASE_DIR / self.db_name}"


settings = Settings()
