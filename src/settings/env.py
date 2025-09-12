from pydantic import AnyUrl, Field, SecretStr, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from utils.constants import ROOT_DIR

ENV_PATH = ROOT_DIR / ".env"


class BaseSettingsEnv(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class BotEnv(BaseSettingsEnv, env_prefix="bot__"):
    token: SecretStr
    payment_token: SecretStr
    admin_ids: list[int] = []

    @field_validator("admin_ids", mode="before")
    @classmethod
    def validate_admin_ids(cls, value):
        if isinstance(value, str):
            return [int(x) for x in value.split(",")]
        return value


class DatabaseEnv(BaseSettingsEnv, env_prefix="db__"):
    scheme: str = "mysql+aiomysql"
    host: str = "mysql"
    port: int = Field(default=3306, ge=1, le=65535)
    user: str = "mysql"
    password: SecretStr | None = None
    name: str = "mysql"

    @property
    def url(self) -> str:
        return str(
            AnyUrl.build(
                scheme=self.scheme,
                username=self.user,
                password=get_secret_value(self.password),
                host=self.host,
                port=self.port,
                path=self.name,
            )
        )


class CacheEnv(BaseSettingsEnv):
    scheme: str = "redis"
    host: str = "localhost"
    port: int = 6379
    password: SecretStr | None = None

    def url(self, db: int = 0) -> str:
        """
        Args:
            db (int): db number in cache (redis - between 0 and 15 )
        Returns:
            str: Cache connection URL
        """
        return str(
            AnyUrl.build(
                scheme=self.scheme,
                password=get_secret_value(self.password),
                host=self.host,
                port=self.port,
                path=str(db),
            )
        )


def get_secret_value(password: SecretStr | None) -> str | None:
    if password is None:
        return None
    return password.get_secret_value()
