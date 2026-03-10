from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache


class RedisConfig(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PREFIX: str
    REDIS_DECODE_RESPONSES: bool
    REDIS_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        arbitrary_types_allowed=True
    )

class DatabaseSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: str
    DB_HOST: str
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        arbitrary_types_allowed=True
    )

    @property
    def get_database_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def get_alembic_database_url(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

class JWTConfig(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MIN: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        arbitrary_types_allowed=True
    )

@lru_cache
def get_redis_config():
    return RedisConfig()

@lru_cache
def get_database_settings():
    return DatabaseSettings()

@lru_cache
def get_jwt_config():
    return JWTConfig()