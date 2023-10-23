from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiobot.db.postgres import DatabaseService
from aiobot.state_machine import ChatState
from aiobot.utils import (
    gen_markup_places,
    gen_markup_shows,
    gen_markup_start,
    send_to_tg,
    to_massage_model,
)
from database import User

from ..local import *


class AioBot:
    def __init__(self, password, token, db_service: DatabaseService):
        self.password = password
        self.bot = Bot(token, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self.db_service = db_service
        self.state = ChatState

        @self.dp.message(CommandStart())
        async def command_start_handler(message: Message, state: FSMContext) -> None:
            """
            This handler receives messages with `/start` command
            """
            user = await self.db_service.get_user(message.chat.id)
            if not user:
                await self.answer_new_user(ENTER_PASSWORD, message, state)
            else:
                await self.answer_init_command(
                    START,
                    STOP,
                    CHANGE_SHOWS,
                    TICKETS_NOW,
                    WELCOME,
                    user.subscription,
                    message,
                    state,
                )

        @self.dp.message(self.state.start)
        async def command_check_password(message: Message, state: FSMContext) -> None:
            if message.text == self.password:
                user = await self.db_service.add_user(message.chat.id)
                await self.answer_init_command(
                    START,
                    STOP,
                    CHANGE_SHOWS,
                    TICKETS_NOW,
                    WELCOME,
                    user.subscription,
                    message,
                    state,
                )
            else:
                await self.answer_new_user(INVALID_PASSWORD, message, state)

        @self.dp.message(self.state.places)
        async def command_from_places(message: Message, state: FSMContext) -> None:
            if message.text == START_TRACKING:
                await self.answer_start_tracking(DATA_REFRESH,
                                                 START, STOP, CHANGE_SHOWS, TICKETS_NOW,
                                                 message, state
                                                 )

            else:
                await self.answer_send_shows(
                    CHOOSE_SHOWS, PLACE_NOT_FOUND, CHOOSE_SCENE_RETURN, START_TRACKING,
                    SELECT,
                    UNSELECT, message, state
                )

        @self.dp.message(self.state.shows)
        async def command_from_shows(message: Message, state: FSMContext) -> None:
            if message.text == START_TRACKING:
                await self.answer_start_tracking(DATA_REFRESH,
                                                 START, STOP, CHANGE_SHOWS, TICKETS_NOW,
                                                 message, state
                                                 )

            elif message.text == CHOOSE_SCENE_RETURN:
                await self.return_answer_send_places(
                    START_TRACKING, DATA_REFRESH, CHOOSE_SCENE, message, state
                )
            else:
                await self.re_answer_send_shows(
                    CHOOSE_SHOWS, SHOWS_NOT_FOUND, CHOOSE_SCENE_RETURN, START_TRACKING,
                    SELECT,
                    UNSELECT, message, state
                )

        @self.dp.message()
        async def command_default(message: Message, state: FSMContext) -> None:
            user = await self.db_service.get_user(message.chat.id)
            if not user:
                await self.answer_new_user(ENTER_PASSWORD, message, state)
                return
            if message.text == START or message.text == STOP:
                await self.answer_start_stop(
                    START,
                    STOP,
                    CHANGE_SHOWS,
                    TICKETS_NOW,
                    TRACKING_OFF,
                    TRACKING_ON,
                    message,
                )
            elif message.text == CHANGE_SHOWS:
                await self.answer_send_places(
                    START_TRACKING, CHOOSE_SCENE, message, state, user
                )
            elif message.text == TICKETS_NOW:
                await self.answer_send_tickets_now(
                    START, STOP, CHANGE_SHOWS, TICKETS_NOW, message, user
                )
            else:
                await self.answer_init_command(
                    START,
                    STOP,
                    CHANGE_SHOWS,
                    TICKETS_NOW,
                    INVALID_COMMAND,
                    user.subscription,
                    message,
                    state,
                )

    async def answer_start_tracking(
            self,
            text: str,
            _start: str,
            stop: str,
            change_shows: str,
            tickets_now: str,
            message: Message,
            state: FSMContext,
    ):
        data_from_state = await state.get_data()
        await self.update_shows(data_from_state, state)
        keyboard = gen_markup_start(
            _start, stop, change_shows, tickets_now, data_from_state['subscription']
        )
        await message.answer(text, reply_markup=keyboard)
        await state.clear()

    async def answer_new_user(
            self, enter_password: str, message: Message, state: FSMContext
    ):
        await message.answer(enter_password)
        await state.set_state(self.state.start)

    async def answer_start_stop(
            self,
            _start: str,
            stop: str,
            change_shows: str,
            tickets_now: str,
            tracking_off: str,
            tracking_on: str,
            message: Message,
    ):
        subscription_status = False if message.text == stop else True
        user = await self.db_service.change_user(message.chat.id, subscription_status)
        answer_text = tracking_off if message.text == stop else tracking_on
        keyboard = gen_markup_start(
            _start, stop, change_shows, tickets_now, user.subscription
        )
        await message.answer(answer_text, reply_markup=keyboard)

    async def answer_send_tickets_now(
            self,
            _start: str,
            stop: str,
            change_shows: str,
            tickets_now: str,
            message: Message,
            user: User,
    ):
        events_data = await self.db_service.get_tickets_now(str(user.id))
        keyboard = gen_markup_start(
            _start=_start,
            stop=stop,
            change_shows=change_shows,
            tickets_now=tickets_now,
            subscription=user.subscription,
        )
        await message.answer(
            send_to_tg(to_massage_model(events_data)), reply_markup=keyboard
        )

    async def answer_send_shows(
            self,
            text: str,
            error: str,
            choose_scene_return: str,
            start_tracking: str,
            select, unselect,
            message: Message,
            state: FSMContext,
    ):
        data_from_state = await state.get_data()
        user_id = data_from_state.get("user_id")
        place_title = message.text
        place_id = data_from_state["places"].get(place_title)
        if not place_id:
            keyboard = gen_markup_places(start_tracking, data_from_state["places"])
            await message.answer(error, reply_markup=keyboard)
            await state.set_state(self.state.places)
            return
        result = await self.db_service.get_shows(place_id, user_id)
        shows = {}
        for show in result:
            shows[show.title[:30]] = {
                "id": str(show.id),
                "subscription": show.user_subscriptions
            }
        keyboard = gen_markup_shows(choose_scene_return, start_tracking, select,
                                    unselect, shows)
        data_from_state['shows'] = shows
        await state.update_data(data_from_state)
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(self.state.shows)

    async def re_answer_send_shows(
            self,
            text: str,
            error: str,
            choose_scene_return: str,
            start_tracking: str,
            select, unselect,
            message: Message,
            state: FSMContext,
    ):
        data_from_state = await state.get_data()
        shows = data_from_state.get("shows")
        current_show = shows.get(message.text[:-2])
        if not current_show:
            keyboard = gen_markup_shows(choose_scene_return, start_tracking, select,
                                        unselect, shows)
            await message.answer(error, reply_markup=keyboard)
            await state.set_state(self.state.shows)
            return
        data_from_state["shows"][message.text[:-2]]['subscription'] = True if not \
            shows[message.text[:-2]]['subscription'] else False
        keyboard = gen_markup_shows(choose_scene_return, start_tracking, select,
                                    unselect, shows)
        await state.update_data(data_from_state)
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(self.state.shows)

    @staticmethod
    async def answer_init_command(
            start,
            stop,
            change_shows,
            tickets_now,
            text: str,
            subscription: bool,
            message: Message,
            state: FSMContext,
    ):
        keyboard = gen_markup_start(
            start, stop, change_shows, tickets_now, subscription
        )
        await message.answer(text, reply_markup=keyboard)
        await state.clear()

    async def answer_send_places(
            self, start_tracking, text: str, message: Message, state: FSMContext,
            user: User | None = None
    ):
        if user:
            data_from_state = {"user_id": str(user.id),
                               "subscription": user.subscription}
        else:
            data_from_state = await state.get_data()
        places = data_from_state.get("places")
        if not places:
            result = await self.db_service.get_places()
            places = {}
            for place in result:
                places[place.title] = str(place.id)
        keyboard = gen_markup_places(start_tracking, places)
        data_from_state["places"] = places
        await state.update_data(data_from_state)
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(self.state.places)

    async def update_shows(self, data: dict, state: FSMContext):
        try:
            await self.db_service.update_user_shows(shows=data['shows'],
                                                    user_id=data['user_id'])
        except KeyError:
            pass
        data['shows'] = {}
        await state.update_data(data)
        return data

    async def return_answer_send_places(
            self, start_tracking, text_one: str, text_two: str, message: Message,
            state: FSMContext
    ):
        data_from_state = await state.get_data()
        places = data_from_state.get("places")
        await self.update_shows(data_from_state, state)

        keyboard = gen_markup_places(start_tracking, places)
        await message.answer(f"{text_one}, {text_two}", reply_markup=keyboard)
        await state.set_state(self.state.places)

    async def start(self):
        await self.dp.start_polling(self.bot)


