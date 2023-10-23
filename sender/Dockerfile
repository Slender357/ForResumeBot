FROM python:3.10

RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

WORKDIR /srс/sender

ENV PYTHONPATH=/srс/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY sender/requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY sender /srс/sender
COPY database /srс/database

CMD python main.py
