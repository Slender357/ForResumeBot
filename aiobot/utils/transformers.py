import re
from datetime import datetime

from database import Event, Place, Show


def get_show_title(raw_show: str):
    pattern = r"\s*-\s*\(\d+\)"
    result = re.sub(pattern, "", raw_show)
    return result


def get_datetime(date: str):
    try:
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def get_datetime_str(date: datetime):
    try:
        return date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def to_massage_model(events_data: list[(Event, Show, Place)]) -> dict:
    formatted_data = {}

    for event, show, place,user_shows in events_data:
        place_title = place.title
        show_title = show.title
        event_datetime = get_datetime_str(event.datetime)
        if place_title not in formatted_data:
            formatted_data[place_title] = {}

        if show_title not in formatted_data[place_title]:
            formatted_data[place_title][show_title] = {}

        if event_datetime not in formatted_data[place_title][show_title]:
            formatted_data[place_title][show_title][event_datetime] = {}

        formatted_data[place_title][show_title][event_datetime] = {
            "url_number": event.url_number,
            "before": event.tickets,
            "now": event.tickets,
        }

    return formatted_data


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
                    text += f"<a href='https://example.ru/show/{data['url_number']}'>{datatime}</a> Билетов: {data['now']}\n"
                else:
                    text += f"<a href='https://example.ru/show/{data['url_number']}'>{datatime}</a> Было:{data['before']} Стало:{data['now']}\n"
            text += f"___________________________________\n\n"
    return text
