from typing import TYPE_CHECKING, cast

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from scheduletelegrambot.settings.config import BotConfig, DatabaseConfig
from scheduletelegrambot.settings.env import (
    ENV_PATH,
    BotEnv,
    CacheEnv,
    DatabaseEnv,
)

if TYPE_CHECKING:
    from collections.abc import Callable


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
    bot: BotSettings = Field(default_factory=cast("Callable[[], BotSettings]", BotSettings))
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheEnv = Field(default_factory=CacheEnv)
