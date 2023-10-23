import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

import aiohttp
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from database import AsyncPostgres, Event, Place, Show, User

from ..broker import RabbitBroker
from ..core import headers

log = logging.getLogger(__name__)


def datetime_for_base(date_time_str: str):
    return datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')


class Checker:
    def __init__(self, broker: RabbitBroker, db: AsyncPostgres, headers: dict,
                 time_sleep: int):
        self.broker = broker
        self.db = db
        self.headers = headers
        self.time_sleep = time_sleep

    async def start_checking(self):
        while True:
            await self.check_tickets()
            await asyncio.sleep(self.time_sleep)

    @asynccontextmanager
    async def get_data_from_db(self):
        async with self.db.async_session() as session:
            result = await session.execute(
                select(User).options(selectinload(User.shows))
                .filter(User.subscription == True)
            )
            users = result.scalars().all()
            yield session, users

    async def check_tickets(self):
        async with self.get_data_from_db() as (session, users):
            if not users:
                return None
            try:
                async with aiohttp.ClientSession(headers=self.headers,
                                                 timeout=aiohttp.ClientTimeout(
                                                         total=10)) as http_session:
                    response = await http_session.get(
                        url="https://example.ru/ticket-api/shows/", headers=headers)
                    if response.status != 200:
                        log.error(response.status)
                        return None
                    result = await self.get_updated_data(await response.json(), session)
                    tasks = self.get_tasks(result, users)
                    await asyncio.gather(*tasks)
            except BaseException as e:
                log.error(e)

    @staticmethod
    def get_place(places: list[Place], hall_id: str) -> Place | None:
        for place in places:
            if place.hall_id == hall_id:
                return place
        return None

    @staticmethod
    def get_show(shows: list[Show], show_title: str,
                 place_id: str) -> Show | None:
        for show in shows:
            if show.title == show_title and show.place_id == place_id:
                return show
        return None

    @staticmethod
    def get_event(events: list[Event], url_number: str) -> Event | None:
        for event in events:
            if event.url_number == url_number:
                return event
        return None

    async def get_updated_data(self, data: list[dict], session):
        update_data = {}
        await session.execute(delete(Event).filter(Event.datetime < datetime.now()))
        await session.commit()
        result = await session.execute(
            select(Place)
        )
        places = result.scalars().all()
        result = await session.execute(
            select(Show)
        )
        shows = result.scalars().all()
        result = await session.execute(
            select(Event)
        )
        events = result.scalars().all()
        for row in data:
            tickets_now = 0 if row['freeSeats'] is None else row['freeSeats']
            url_number = row['showId']
            place_title = row['hallName']
            hall_id = row['hallId']
            show_title = row['showName']
            event_datetime = f"{row['specDate']} {row['startTime']}"
            place = self.get_place(places, hall_id)
            if not place:
                place = Place(id=uuid.uuid4(), hall_id=hall_id, title=place_title)
                session.add(place)
                places.append(place)
            show = self.get_show(shows, show_title, place.id)
            if not show:
                show = Show(
                    id=uuid.uuid4(), title=show_title, place_id=place.id
                )
                session.add(show)
                shows.append(show)
            event = self.get_event(events, url_number)
            if not event:
                event = Event(
                    id=uuid.uuid4(),
                    datetime=datetime_for_base(event_datetime),
                    show_id=show.id,
                    url_number=url_number,
                    tickets=tickets_now
                )
                session.add(event)
                events.append(event)
                tickets_before = 0
                await session.commit()
            else:
                tickets_before = event.tickets
                event.tickets = tickets_now
                await session.commit()
            if tickets_now > (tickets_before + tickets_now // 10):
                shows_id = str(show.id)
                if shows_id not in update_data:
                    update_data[shows_id] = {
                        "place": place.title,
                        "show": show.title,
                        "events": []
                    }
                update_data[shows_id]["events"].append(
                    {
                        "datetime": event_datetime,
                        "url_number": url_number,
                        "before": tickets_before,
                        "now": tickets_now,
                    }
                )
        return update_data

    def get_tasks(self, result, users):
        tasks = []
        for user in users:
            tasks.append(
                asyncio.create_task(self.create_task(result, user))
            )
        return tasks

    async def create_task(self,
                          result, user
                          ):
        formatted_data = {}
        for show in user.shows:
            show_id = str(show.show_id)
            row = result.get(show_id)

            if row:
                place = row["place"]
                show = row["show"]
                if place not in formatted_data:
                    formatted_data[place] = {}
                formatted_data[place][show] = {}
                for event in row["events"]:
                    formatted_data[place][show][event["datetime"]] = {
                        "url_number": event["url_number"],
                        "before": event["before"],
                        "now": event["now"],
                    }
        if formatted_data:
            await self.broker.send_in_queue({"chat_id": user.chat_id,
                                             "message": formatted_data})
