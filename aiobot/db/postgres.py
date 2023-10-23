import uuid

from sqlalchemy import select, and_, delete, asc
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncPostgres, Event, Place, Show, User, UsersShows


class DatabaseService:
    def __init__(self, db: AsyncPostgres):
        self.db = db

    @staticmethod
    async def _get_user(session: AsyncSession, chat_id: int):
        result = await session.execute(select(User).filter(User.chat_id == chat_id))
        user = result.scalars().first()
        if not user:
            return None
        return user

    async def get_user(self, chat_id: int):
        async with self.db.async_session() as session:
            return await self._get_user(session, chat_id)

    async def add_user(self, chat_id: int):
        async with self.db.async_session() as session:
            user = User(id=uuid.uuid4(), chat_id=chat_id, subscription=False)
            session.add(user)
            await session.commit()
        return user

    async def change_user(self, chat_id: int, subscription: bool):
        async with self.db.async_session() as session:
            user = await self._get_user(session, chat_id)
            if not user:
                return None
            user.subscription = subscription
            await session.commit()
        return user

    async def get_places(self):
        async with self.db.async_session() as session:
            result = await session.execute(select(Place).order_by(asc(Place.title)))
            places = result.scalars().all()
        return places

    async def get_shows(self, place_id: str, user_id: int):
        async with self.db.async_session() as session:
            result = await session.execute(
                select(Show)
                .filter(Show.place_id == place_id).order_by(asc(Show.title))
            )
            shows = result.scalars().all()
            result = await session.execute(
                select(UsersShows.show_id)
                .filter(UsersShows.user_id == user_id)
            )
            user_subscribed_show_ids = set(
                result.scalars().all()
            )
            for show in shows:
                show.user_subscriptions = show.id in user_subscribed_show_ids
        return shows

    async def update_user_shows(
            self, shows: dict, user_id: str
    ):
        async with self.db.async_session() as session:
            add_shows = []
            show_ids = []
            for show in shows.values():
                if show['subscription']:
                    add_shows.append(UsersShows(user_id=user_id, show_id=show['id']))
                show_ids.append(show['id'])
            condition = and_(UsersShows.user_id == user_id,
                             UsersShows.show_id.in_(show_ids))

            delete_query = delete(UsersShows).where(condition)
            await session.execute(delete_query)
            await session.commit()
            session.add_all(add_shows)
            await session.commit()

    async def get_tickets_now(self, user_id: str):
        async with self.db.async_session() as session:
            result = await session.execute(
                select(Event, Show, Place, UsersShows)
                .join(Show, Event.show_id == Show.id)
                .join(Place, Show.place_id == Place.id)
                .join(UsersShows, and_(UsersShows.user_id == user_id,
                                       UsersShows.show_id == Show.id)).order_by(asc(Place.title))
            )
            events = result.all()
        return events
