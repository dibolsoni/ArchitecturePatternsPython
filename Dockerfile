ARG APP_IMAGE=python:3.11-slim-buster
FROM $APP_IMAGE AS base
FROM base as builder

RUN mkdir -p /allocation
WORKDIR /allocation

COPY requirements.txt requirements.txt
RUN pip install  -r requirements.txt

COPY allocation/ .

COPY ./tests /tests/

RUN pip install -e ./

ENV FLASK_APP=/allocation/src/entrypoints/api.py FLASK_DEBUG=1 PYTHONUNBUFFERED=1
CMD flask run --host=0.0.0.0 --port=80

EXPOSE 8000
