from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .core import pg_config


class AsyncPostgres:
    def __init__(self):
        self.url = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            pg_config.db_user,
            pg_config.db_password,
            pg_config.db_host,
            pg_config.db_port,
            pg_config.db_name,
        )
        self.async_session: async_sessionmaker[AsyncSession] | None = None
        self.engine: AsyncEngine | None = None

    async def __aenter__(self):
        self.engine = create_async_engine(self.url)
        self.async_session = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.engine.dispose()
