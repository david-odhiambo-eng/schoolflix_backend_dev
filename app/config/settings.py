from datetime import timedelta
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic.networks import RedisDsn

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"))
    VERSION: str
    DATABASE_URI: str
    REDIS_URI: RedisDsn = "redis://localhost:6379/0"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30


    @computed_field
    @property
    def DATABASE_URL(self)->str:
        return MultiHostUrl(url=self.DATABASE_URI).unicode_string()

    @computed_field()
    @property
    def ACCESS_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    @computed_field()
    @property
    def REFRESH_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_DAYS)

    @computed_field()
    @property
    def REDIS_URL(self)-> str:
        return self.REDIS_URI



settings = Config()

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models.index", "aerich.models"],
            "default_connection": "default",
        },
    },
}