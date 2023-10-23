import logging
from abc import ABC

import aio_pika
import orjson

log = logging.getLogger(__name__)


class AbstractBroker(ABC):
    async def start(self) -> None:
        pass

    async def send_in_queue(self, message: dict) -> bool:
        pass

    async def close(self) -> None:
        pass


class RabbitBroker(AbstractBroker):
    def __init__(self, rabbitmq_host, queue):
        self.rabbitmq_host = rabbitmq_host
        self._connection = None
        self._channel = None
        self.queue = queue

    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self.rabbitmq_host)
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(self.queue, durable=True)

    async def send_in_queue(self, message: dict) -> bool:
        if not message:
            return False
        try:
            if self._channel is not None:
                await self._channel.default_exchange.publish(
                    aio_pika.Message(body=orjson.dumps(message), delivery_mode=2),
                    routing_key=self.queue,
                )
            else:
                raise
            return True
        except aio_pika.exceptions.AMQPError as e:
            log.error(e)
            return False

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
