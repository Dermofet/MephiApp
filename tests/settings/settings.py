from functools import lru_cache
from typing import Optional

from dotenv import find_dotenv
from pydantic import BaseSettings, PostgresDsn


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}


class Settings(BaseSettings):
    class Config:
        env_file_encoding = 'utf-8'

    DBUSER: str
    DBPASS: str
    DBHOST: str
    DBPORT: int
    DBNAME: str

    @property
    def dsn(self):
        return f"postgresql+asyncpg://{self.DBUSER}:{self.DBPASS}@{self.DBHOST}:{self.DBPORT}/{self.DBNAME}"

@lru_cache()
def get_settings(envfile: str = "tests/.env"):
    return Settings(_env_file=find_dotenv(envfile))