from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath
from functools import cache


class Settings(BaseSettings):
    telegram_bot_secret: str = ""
    image_folder: DirectoryPath | None = None
    token_secret_key: str = ""
    dev_mode: bool = False
    db_path: DirectoryPath | None = None

    otel_enabled: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert None to empty string for compatibility with existing code
        self.image_folder = self.image_folder or ""
        self.db_path = self.db_path or ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@cache
def get_settings():
    return Settings()
