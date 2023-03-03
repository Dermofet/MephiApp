from __future__ import annotations

from functools import lru_cache
from typing import Optional

from dotenv import find_dotenv
from pydantic import BaseSettings, validator


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
    LANGS: list[str]


@lru_cache()
def get_config(env_file: str = ".env") -> Config:
    return Config(_env_file=find_dotenv(env_file))
