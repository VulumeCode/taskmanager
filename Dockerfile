FROM python:3.12-alpine-3.20
RUN mkdir /app
COPY . /app
RUN pip install /app/