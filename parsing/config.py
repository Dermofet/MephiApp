from __future__ import annotations

from functools import lru_cache
from typing import Optional

from dotenv import find_dotenv
from pydantic import BaseSettings, PostgresDsn, validator


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}


class _Settings(BaseSettings):
    class Config:
        env_file_encoding = "utf-8"


class Config(_Settings):
    # Parsers
    MEPHI_SCHEDULE_URL: str
    HOME_MEPHI_URL: str
    MEPHI_ROOM_URL: str
    MEPHI_TEACHERS_URL: str

    # Translating
    FOREIGN_LANGS: list[str]

    # Postgres
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    SQLALCHEMY_DATABASE_URI: Optional[AsyncPostgresDsn]

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return AsyncPostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )


@lru_cache()
def get_config(env_file: str = ".env") -> Config:
    return Config(_env_file=find_dotenv(env_file))