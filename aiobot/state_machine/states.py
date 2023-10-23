from aiogram.fsm.state import State, StatesGroup


class ChatState(StatesGroup):
    start = State()
    places = State()
    shows = State()
    events = State()
