FROM python:3 as base

FROM base as builder
RUN apt-get update

FROM builder as pip
COPY requirements.txt code/requirements.txt
RUN pip install -r code/requirements.txt

FROM pip
COPY . code/