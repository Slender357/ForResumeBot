import asyncio
import logging

from checker.broker import RabbitBroker
from checker.core import LOGGING, config, headers
from checker.services import Checker
from database import AsyncPostgres

log = logging.getLogger(__name__)


async def main():
    rabbit = RabbitBroker(rabbitmq_host=config.rabbit_url, queue=config.queue)
    async with AsyncPostgres() as db:
        await rabbit.start()
        handler = Checker(broker=rabbit, db=db, headers=headers, time_sleep=config.time_sleep)
        try:
            await handler.start_checking()
        finally:
            await rabbit.close()


if __name__ == "__main__":
    logging.basicConfig(**LOGGING)
    asyncio.run(main())
