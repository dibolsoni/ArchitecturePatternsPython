FROM python:3.11-slim-buster

RUN mkdir -p /code
WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip install  -r requirements.txt
COPY ./*.py .
COPY ./adapters ./adapters/
COPY ./domain ./domain/
COPY ./entrypoints ./entrypoints/
COPY ./service_layer ./service_layer/
COPY ./tests ./tests/

CMD ["python", "-m", "entrypoints.api"]

EXPOSE 8000
