import asyncio
import logging

from aiogram import Bot
from aiogram.enums import ParseMode

from database import AsyncPostgres, User

log = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, token: str, db: AsyncPostgres):
        self.bot = Bot(token, parse_mode=ParseMode.HTML)
        self.db = db

    async def send_message(self, message: dict):
        try:
            await self.bot.send_message(message['chat_id'],
                                        self.send_to_tg(message['message']))
        except BaseException as e:
            log.error(e)
        return True

    def get_tasks_notification(self, users: list[User], text: str):
        tasks = []
        for user in users:
            tasks.append(asyncio.create_task(self.bot.send_message(user.chat_id, text)))
        return tasks

    @staticmethod
    def send_to_tg(message: dict) -> str:
        text = ""
        if message == {}:
            text += "Билетов нет"
            return text
        for place, shows in message.items():
            text += f"⬇️<b>{place}</b>⬇️ \n\n"
            for show, events in shows.items():
                text += f"<b>{show}:</b> \n"
                for datatime, data in events.items():
                    if data["before"] == data["now"]:
                        text += f"<a href='https://example.ru/show/" \
                                f"{data['url_number']}'>{datatime}</a> " \
                                f"Билетов: {data['now']}\n"
                    else:
                        text += f"<a href='https://example.ru/show/" \
                                f"{data['url_number']}'>{datatime}</a> " \
                                f"Было:{data['before']} Стало:{data['now']}\n"
                text += f"___________________________________\n\n"
        return text
