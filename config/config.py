from __future__ import annotations

from functools import lru_cache

from dotenv import find_dotenv
from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    class Config:
        env_file_encoding = "utf-8"


class Config(_Settings):
    # Debug
    DEBUG: bool

    # Backend
    BACKEND_TITLE: str
    BACKEND_DESCRIPTION: str
    BACKEND_PREFIX: str

    BACKEND_HOST: str
    BACKEND_LOCALHOST: str
    BACKEND_PORT: int
    BACKEND_RELOAD: bool

    # Postgres
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


@lru_cache()
def get_config(env_file: str = ".env") -> Config:
    return Config(_env_file=find_dotenv(env_file))


