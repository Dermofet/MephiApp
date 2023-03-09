from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Optional

from dotenv import find_dotenv
from pydantic import BaseSettings, PostgresDsn, validator


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}


class _Settings(BaseSettings):
    class Config:
        env_file_encoding = "utf-8"


# @singleton
class Config(_Settings):
    # Postgres
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Celery
    C_FORCE_ROOT: bool
    CELERY_BROKER_URL: str

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
