FROM python:3.9-slim

ARG API_KEY
ENV API_KEY=$API_KEY

ARG VERSION
ENV B_NUM=$VERSION

ARG COLOR
ENV BG_COLOR=$COLOR

WORKDIR ~/

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn --bind 0.0.0.0:5000 wsgi:app

