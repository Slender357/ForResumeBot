import asyncio
import logging

from database import AsyncPostgres
from sender.broker import RabbitMQConnect
from sender.core import LOGGING, config
from sender.services import MessageHandler, RabbitMQConsumer

log = logging.getLogger(__name__)


async def main():
    async with AsyncPostgres() as db:
        rabbit = RabbitMQConnect(amqp_url=config.rabbit_url)
        await rabbit.connect()
        consumer = RabbitMQConsumer(
            queue_name=config.queue, connection=rabbit.connection
        )
        handler = MessageHandler(token=config.token, db=db)
        try:
            await consumer.start_consuming(handler.send_message)
        finally:
            await rabbit.close()


if __name__ == "__main__":
    logging.basicConfig(**LOGGING)
    asyncio.run(main())
