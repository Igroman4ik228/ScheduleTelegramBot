from json import load
from os import getcwd
from os.path import exists, join

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseModel):
    token: str = ""
    payment_token: str = ""
    admin_ids: list[int] = Field(default_factory=list)
    rate_limit: float = Field(
        default=0.2,
        ge=0,
        description="Rate limit for throttling control"
    )

    @field_validator("admin_ids", mode="before")
    @classmethod
    def validate_admin_ids(cls, value):
        if isinstance(value, str):
            return [int(x) for x in value.split(",")]
        return value


class DatabaseSettings(BaseModel):
    host: str = "mysql"
    port: int = 3306
    user: str = "mysql"
    password: str | None = None
    name: str = "mysql"

    echo: bool = False
    pre_ping: bool = True
    pool_size: int = 50
    max_overflow: int = 10

    @property
    def url(self) -> str:
        if self.password:
            return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        return f"mysql+aiomysql://{self.user}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseModel):
    host: str = "redis"
    port: int = 6379
    password: str | None = None

    def url(self, db: int = Field(default=0, ge=0, le=15)) -> str:
        """
        Args:
            db (int): DB number (0-15)
        Returns:
            str: Redis connection URL
        """
        if self.password:
            return f"redis://{self.host}:{self.password}{self.port}/{db}"
        return f"redis://{self.host}:{self.port}/{db}"


class LoggerSettings(BaseModel):
    path: str = join(getcwd(), "logs")
    config_file_name: str = "logger.conf.json"

    @property
    def logger_conf(self) -> dict:
        file_path = join(self.path, self.config_file_name)

        if not file_path.endswith(".json"):
            raise ValueError("Logger config file must be a json file")

        if not exists(file_path):
            return {
                'version': 1,
                "disable_existing_loggers": False,
                'handlers': {
                    'console': {
                        'class': 'logging.StreamHandler',
                        'formatter': 'default'
                    },
                },
                'formatters': {
                    'default': {
                        'format': '(%(levelname)s) %(asctime)s - %(name)s: %(message)s',
                        'datefmt': '%d-%m-%Y %H:%M:%S'
                    },
                },
                'root': {
                    'handlers': ['console'],
                    'level': 'INFO'
                },
            }

        with open(file_path, encoding="utf-8") as file:
            return load(file)

    def configure(self):
        from logging import NullHandler, getLogger
        from logging.config import dictConfig

        dictConfig(self.logger_conf)

        # Disable sqlalchemy engine logs
        getLogger("sqlalchemy.engine.Engine").handlers = [
            NullHandler()
        ]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.example", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot = BotSettings()
    db = DatabaseSettings()
    redis = RedisSettings()
    logger = LoggerSettings()

    debug: bool = False


settings = Settings()
