# Dockerfile

# Pull base image
FROM python:3.10-alpine

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN apk update \
     && apk add --virtual build-essential gcc python3-dev musl-dev \
     && apk add postgresql-dev \
     && pip install psycopg2

# Install dependencies
# RUN pip install pipenv
# COPY Pipfile Pipfile.lock /code/
# RUN pipenv install wheel
# RUN pipenv install --system
COPY ./requirements.txt .
RUN pip install -r requirements.txt 


# Copy project
COPY . .
RUN python manage.py collectstatic --noinput

RUN adduser -D myuser
USER myuser

CMD gunicorn fuzzyaitest.wsgi:application --bind 0.0.0.0:$PORT