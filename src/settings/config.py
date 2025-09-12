from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    SettingsConfigDict,
)

from utils.constants import ROOT_DIR

CONFIG_DIR = ROOT_DIR / "configs"
CONFIG_PATH = CONFIG_DIR / "config.json"


class BaseSettingsConfig(BaseSettings):
    model_config = SettingsConfigDict(
        json_file=CONFIG_PATH,
        json_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> tuple:
        return (
            JsonConfigSettingsSource(settings_cls),
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


class BotConfig(BaseSettingsConfig):
    rate_limit: float = Field(
        default=0.2, ge=0, description="Rate limit for throttling control"
    )


class DatabaseConfig(BaseSettingsConfig):
    echo: bool = False
    pre_ping: bool = True
    pool_size: int = Field(default=50, ge=1)
    max_overflow: int = Field(default=10, ge=1)
