from json import JSONDecodeError, load
from os import getcwd
from os.path import exists, join

from pydantic import BaseModel, Field, MySQLDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseModel):
    """Настройки бота Telegram."""
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

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v and not settings.debug:
            raise ValueError("Token cannot be empty in production mode")
        return v


class DatabaseSettings(BaseModel):
    scheme: str = "mysql+aiomysql"
    host: str = "mysql"
    port: int = Field(default=3306, ge=1, le=65535)
    user: str = "mysql"
    password: str | None = None
    name: str = "mysql"

    echo: bool = False
    pre_ping: bool = True
    pool_size: int = Field(default=50, ge=1)
    max_overflow: int = Field(default=10, ge=1)

    @property
    def url(self) -> str:
        return str(
            MySQLDsn.build(
                scheme=self.scheme,
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.name
            )
        )


class RedisSettings(BaseModel):
    scheme: str = "redis"
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
        return str(
            RedisDsn.build(
                scheme=self.scheme,
                password=self.password,
                host=self.host,
                port=self.port,
                path=str(db)
            )
        )


class LoggerSettings(BaseModel):
    path: str = join(getcwd(), "logs")
    config_file_name: str = Field(
        default="logger.conf.json",
        pattern=r".*\.json$"
    )

    @property
    def logger_conf(self):
        file_path = join(self.path, self.config_file_name)

        if not exists(file_path):
            return self._get_default_config()
        try:
            with open(file_path, encoding="utf-8") as file:
                return load(file)
        except JSONDecodeError:
            return self._get_default_config()

    def _get_default_config(self):
        """Возвращает конфигурацию логгера по умолчанию."""
        return {
            'version': 1,
            "disable_existing_loggers": False,
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default'
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'filename': join(self.path, 'app.log'),
                    'formatter': 'default'
                }
            },
            'formatters': {
                'default': {
                    'format': '(%(levelname)s) %(asctime)s - %(name)s: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
            },
            'root': {
                'handlers': ['console', 'file'],
                'level': 'INFO'
            },
        }

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

    bot: BotSettings = BotSettings()
    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    logger: LoggerSettings = LoggerSettings()

    debug: bool = False


settings = Settings()
settings.logger.configure()
