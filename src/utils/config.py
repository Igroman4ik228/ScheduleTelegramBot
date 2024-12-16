from json import load
from os import getcwd
from os.path import join

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class BotSettings(EnvBaseSettings):
    BOT_TOKEN: str
    RATE_LIMIT: int | float = 0.2  # for throttling control
    ADMIN_IDS: list[int] = []
    PAYMENT_TOKEN: str


class DBSettings(EnvBaseSettings):
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_USER: str = "mysql"
    DB_PASS: str | None = None
    DB_NAME: str = "mysql"

    @property
    def database_url(self) -> str:
        if self.DB_PASS:
            return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"mysql+aiomysql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class RedisSettings(EnvBaseSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASS: str | None = None


class LoggerSettings(EnvBaseSettings):
    LOG_PATH: str = join(getcwd(), "logs")

    @property
    def logger_conf(self) -> dict:
        file_path = join(self.LOG_PATH, "logger.conf.json")
        try:
            with open(file_path, encoding="utf-8") as file:
                log_config = load(file)
        except FileNotFoundError:
            log_config = {'version': 1}
        return log_config


class Settings(BotSettings, DBSettings, RedisSettings, LoggerSettings):
    DB_ECHO: bool = False
    DEBUG: bool = False


settings = Settings()
