import os

import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv.load_dotenv()


class AppSettings(BaseSettings):
    queue: str = "queue"
    rabbit_url: str = "url"
    token: str = "token"

    model_config = SettingsConfigDict(env_file="sender/.env", env_file_encoding="utf-8")


config = AppSettings()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
