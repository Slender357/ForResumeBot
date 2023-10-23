import aio_pika


class RabbitMQConnect:
    def __init__(self, amqp_url):
        self.amqp_url = amqp_url
        self.connection = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.amqp_url)

    async def close(self):
        if self.connection is not None:
            await self.connection.close()
