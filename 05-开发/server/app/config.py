"""应用配置，从环境变量读取。"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/diaolema.db"
    QWEATHER_API_KEY: str = ""
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""
    WECHAT_MASTER_KEY: str = ""
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://127.0.0.1:8080,http://localhost:8080"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
