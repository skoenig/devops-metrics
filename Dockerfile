FROM python:3.13-slim-bookworm as base

WORKDIR /app

FROM base as builder
ENV POETRY_VERSION=1.6.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

RUN python3 -m venv $POETRY_HOME \
    && $POETRY_HOME/bin/pip install poetry==${POETRY_VERSION} \
    && $POETRY_HOME/bin/poetry --version
ENV PATH="$POETRY_HOME/bin:$PATH"

COPY pyproject.toml poetry.lock /app

RUN poetry install --without dev

FROM base
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq -y update \
    && apt-get -qq -y install --no-install-recommends git \
    && apt-get -qq -y clean \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

COPY pipeline-metrics.py entrypoint.sh /app

ENTRYPOINT /app/entrypoint.sh
