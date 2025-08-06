FROM python:3.11.6-alpine3.18
LABEL maintainer="kol230305@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR app/

RUN apk add --no-cache \
    gettext \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    python3-dev \
    build-base \
    bash

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /media

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

RUN chown -R my_user /media
RUN chmod -R 755 /media