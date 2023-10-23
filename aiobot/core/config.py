import os

import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv.load_dotenv()


class AppSettings(BaseSettings):
    token: str = "queue"
    app_password: str = "url"

    model_config = SettingsConfigDict(env_file="app/.env", env_file_encoding="utf-8")


config = AppSettings()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
