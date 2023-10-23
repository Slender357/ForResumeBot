FROM python:3.10

RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

WORKDIR /src/aiobot

ENV PYTHONPATH=/src/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY aiobot/requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY aiobot /src/aiobot
COPY database /src/database
COPY migration /src/migration
COPY alembic.ini /src/alembic.ini

WORKDIR /src

CMD alembic upgrade head && python aiobot/main.py
