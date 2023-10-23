import asyncio
import logging

from aiobot.core import LOGGING, config
from aiobot.db import DatabaseService
from aiobot.telegram import AioBot
from database import AsyncPostgres

log = logging.getLogger(__name__)


async def main() -> None:
    async with AsyncPostgres() as db:
        sessions = DatabaseService(db)
        bot = AioBot(config.app_password, config.token, sessions)
        await bot.start()


if __name__ == "__main__":
    logging.basicConfig(**LOGGING)
    asyncio.run(main())
