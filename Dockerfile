# syntax=docker/dockerfile:1

FROM python:3.8-slim

ENV DJANGO_SETTINGS_MODULE=init.settings.beta

WORKDIR /usr/src/app

COPY ./likeminds_payments/requirements.txt requirements.txt

RUN python3 -m venv /opt/venv

RUN . /opt/venv/bin/activate && pip3 install -r requirements.txt --no-cache-dir

ADD ./likeminds_payments $WORKDIR

ADD https://beta-likeminds-media.s3.ap-south-1.amazonaws.com/environment/Skulk-Beta-Dot-Env/.env ./init/settings/
