# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# libpq for psycopg, gettext for Django's translation machinery (LANGUAGE_CODE=pt),
# build-essential for any wheel that still needs compiling on this platform.
RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        libpq-dev \
        gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements ./requirements
RUN pip install --no-cache-dir -r requirements/local.txt

COPY compose/local/django/entrypoint /entrypoint
COPY compose/local/django/start /start
RUN sed -i 's/\r$//g' /entrypoint /start && chmod +x /entrypoint /start

COPY . /app

ENTRYPOINT ["/entrypoint"]
