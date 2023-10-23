from aiogram.types import KeyboardButton, ReplyKeyboardMarkup



def gen_markup_start(
        _start: str, stop: str, change_shows: str, tickets_now: str, subscription: bool
) -> ReplyKeyboardMarkup:
    subscription_bt_text = _start if not subscription else stop
    subscription_bt = KeyboardButton(text=subscription_bt_text)
    change_bt = KeyboardButton(text=change_shows)
    tickets_now = KeyboardButton(text=tickets_now)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[subscription_bt], [change_bt], [tickets_now]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


def gen_markup_places(start_tracking: str, places: dict) -> ReplyKeyboardMarkup:
    keyboard_buttons = [KeyboardButton(text=place) for place in places.keys()]
    keyboard_buttons.insert(0, KeyboardButton(text=start_tracking))
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[btn] for btn in keyboard_buttons], resize_keyboard=True
    )
    return keyboard


def gen_markup_shows(
        choose_scene_return: str, start_tracking: str, select, unselect,
        shows: dict[dict]
) -> ReplyKeyboardMarkup:
    keyboard_buttons = [
        KeyboardButton(
            text=f"{title} {select if not show['subscription'] else unselect}")
        for title, show in shows.items()
    ]
    keyboard_buttons.insert(0, KeyboardButton(text=start_tracking))
    keyboard_buttons.insert(0, KeyboardButton(text=choose_scene_return))
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[btn] for btn in keyboard_buttons], resize_keyboard=True
    )
    return keyboard
