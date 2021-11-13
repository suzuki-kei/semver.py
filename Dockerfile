FROM python:3.10.0

RUN mkdir /app
WORKDIR /app
VOLUME /app

ENV PYTHONPATH=/app/semver

COPY requirements.txt .
RUN pip install -r requirements.txt

