FROM python:3.12.7-alpine3.20
RUN mkdir /app
COPY . /app
RUN pip install /app/