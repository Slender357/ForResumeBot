FROM python:3.10

RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

WORKDIR /srс/checker

ENV PYTHONPATH=/srс/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY checker/requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY checker /srс/checker
COPY database /srс/database

CMD python main.py
