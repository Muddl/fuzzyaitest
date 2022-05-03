# Dockerfile

# Pull base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN apk update \
     && apk add --virtual build-essential gcc python3-dev musl-dev \
     && apk add postgresql-dev
# Set work directory
WORKDIR /code

# Install dependencies
RUN pip install pipenv
COPY Pipfile Pipfile.lock /code/
RUN pipenv install wheel
RUN pipenv install --system

# Copy project
COPY . /code/


RUN adduser -D myuser
USER myuser

CMD gunicorn fuzzyaitest.wsgi:application --bind 0.0.0.0:$PORT