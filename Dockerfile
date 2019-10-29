FROM python:3 as base

FROM base as builder
RUN apt-get update

FROM builder as pip

# Because context is set in docker compose, we're already in /scraper when we start the build
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

FROM pip

COPY . .
CMD python app.py