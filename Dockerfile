FROM python:3.8.0-alpine as base

FROM base as pip
COPY requirements.txt code/requirements.txt
RUN pip install -r code/requirements.txt

FROM pip
COPY . code/

WORKDIR /code
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]