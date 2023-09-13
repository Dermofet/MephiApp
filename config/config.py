from __future__ import annotations

from functools import lru_cache
from typing import Any, List, Optional

from dotenv import find_dotenv
from pydantic import AmqpDsn, Field, HttpUrl, PostgresDsn, RedisDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class AsyncPostgresDns(PostgresDsn):
    allowed_schemas = ["postgres+asyncpg", "postgresql+asyncpg"]

class _Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8")

class Config(_Settings):
    # Debug
    DEBUG: bool = Field(..., description="Debug mode")

    # Backend
    BACKEND_TITLE: str = Field(..., description="Backend title")
    BACKEND_DESCRIPTION: str = Field(..., description="Backend description")
    BACKEND_PREFIX: str = Field(..., description="Backend prefix")

    BACKEND_HOST: str = Field(..., description="Backend host")
    BACKEND_LOCALHOST: str = Field(..., description="Backend localhost")
    BACKEND_PORT: int = Field(..., description="Backend port")
    BACKEND_RELOAD: bool = Field(..., description="Backend reload")

    # Postgres
    POSTGRES_USER: str = Field(..., description="Postgres user")
    POSTGRES_PASSWORD: str = Field(..., description="Postgres password")
    POSTGRES_SERVER: str = Field(..., description="Postgres server")
    POSTGRES_PORT: int = Field(..., description="Postgres port")
    POSTGRES_DB: str = Field(..., description="Postgres database")
    LOCAL_POSTGRES_SERVER: str = Field(..., description="Postgres server for local using")

    DB_URI: Optional[AsyncPostgresDns] = Field(None, description="Postgres uri for docker contaibers", validate_default=True)
    LOCAL_DB_URI: Optional[AsyncPostgresDns] = Field(None, description="Postgres uri for alembic", validate_default=True)

    # Parsers
    MEPHI_SCHEDULE_URL: HttpUrl = Field(..., description="Mephi schedule url")
    HOME_MEPHI_URL: HttpUrl = Field(..., description="Home mephi url")
    MEPHI_ROOM_URL: HttpUrl = Field(..., description="Mephi room url")
    MEPHI_TEACHERS_URL: HttpUrl = Field(..., description="Mephi teachers url")
    MEPHI_AUTH_URL: HttpUrl = Field(..., description="Mephi auth url")
    MEPHI_AUTH_SERVICE_URL: HttpUrl = Field(..., description="Mephi auth service url")
    MEPHI_LOGIN: str = Field(..., description="Mephi login")
    MEPHI_PASSWORD: str = Field(..., description="Mephi password")

    # Translating
    FOREIGN_LANGS: List[str] = Field(..., description="Foreign langs")

    # News
    MEPHI_NEWS_PAGE_URL: HttpUrl = Field(..., description="Mephi news page url")
    MEPHI_URL: HttpUrl = Field(..., description="Mephi url")

    # Celery
    CELERY_NAME: str = Field(..., description="Celery name")

    # Redis
    REDIS_HOST: str = Field(..., description="Redis host")
    REDIS_PORT: int = Field(..., description="Redis port")
    REDIS_USER: str = Field(..., description="Redis user")
    REDIS_PASS: str = Field(..., description="Redis password")
    REDIS_DB: int = Field(..., description="Redis db")

    REDIS_URI: Optional[RedisDsn] = Field(None, description="Redis uri", validate_default=True)

    # RabbitMQ
    RABBITMQ_HOST: str = Field(..., description="RabbitMQ host")
    RABBITMQ_PORT: int = Field(..., description="RabbitMQ port")
    RABBITMQ_USER: str = Field(..., description="RabbitMQ user")
    RABBITMQ_PASS: str = Field(..., description="RabbitMQ password")

    RABBITMQ_URI: Optional[AmqpDsn] = Field(None, description="RabbitMQ uri", validate_default=True)

    @field_validator("DB_URI", mode="before")
    def create_db_uri(cls, v: Optional[str], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return AsyncPostgresDns.build(
            scheme="postgresql+asyncpg",
            username=info.data['POSTGRES_USER'],
            password=info.data['POSTGRES_PASSWORD'],
            host=info.data['POSTGRES_SERVER'],
            port=info.data['POSTGRES_PORT'],
            path=info.data['POSTGRES_DB']
        )

    @field_validator("LOCAL_DB_URI", mode="before")
    def create_alembic_db_uri(cls, v: Optional[str], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return AsyncPostgresDns.build(
            scheme="postgresql+asyncpg",
            username=info.data['POSTGRES_USER'],
            password=info.data['POSTGRES_PASSWORD'],
            host=info.data['LOCAL_POSTGRES_SERVER'],
            port=info.data['POSTGRES_PORT'],
            path=info.data['POSTGRES_DB']
        )

    @field_validator("REDIS_URI", mode="before")
    def create_redis_uri(cls, v: Optional[str], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=info.data['REDIS_HOST'],
            port=info.data['REDIS_PORT'],
            username=info.data['REDIS_USER'],
            password=info.data['REDIS_PASS'],
            path=str(info.data['REDIS_DB'])
        )

    @field_validator("RABBITMQ_URI", mode="before", check_fields=False)
    def create_rabbitmq_uri(cls, v: Optional[str], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return AmqpDsn.build(
            scheme="amqp",
            host=info.data['RABBITMQ_HOST'],
            port=info.data['RABBITMQ_PORT'],
            username=info.data['RABBITMQ_USER'],
            password=info.data['RABBITMQ_PASS'],
        )


@lru_cache()
def get_config(env_file: str = ".env") -> Config:
    return Config(_env_file=find_dotenv(env_file))


