from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from settings.config import BotConfig, DatabaseConfig
from settings.env import ENV_PATH, BotEnv, CacheEnv, DatabaseEnv


class BotSettings(BotEnv, BotConfig):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="bot__",
    )


class DatabaseSettings(DatabaseEnv, DatabaseConfig):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="db__",
    )


class Settings(BaseSettings):
    bot: BotSettings = BotSettings()
    db: DatabaseSettings = DatabaseSettings()
    cache: CacheEnv = CacheEnv()
