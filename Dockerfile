FROM python:3 as base

FROM base as builder
RUN apt-get update

FROM builder as pip
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

FROM pip
COPY . .
CMD gunicorn --workers=1 app:app --bind 0.0.0.0:8000