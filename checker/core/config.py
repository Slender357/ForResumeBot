import os

import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv.load_dotenv()

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "ru-RU,ru;q=0.9",
    "sec-ch-ua": "\"Google Chrome\";v=\"107\", \"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}


class AppSettings(BaseSettings):
    queue: str = "queue"
    rabbit_url: str = "url"
    time_sleep: int = 10

    model_config = SettingsConfigDict(
        env_file="checker/.env", env_file_encoding="utf-8"
    )


config = AppSettings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
