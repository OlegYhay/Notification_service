
FROM python:3.10.5

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /Notification_service/main

COPY Pipfile Pipfile.lock /Notification_service/
RUN pip install pipenv && pipenv install --system
RUN pip install psycopg2

COPY . /Notification_service/