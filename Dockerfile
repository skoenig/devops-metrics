FROM python:3.11

ENV POETRY_HOME=/opt/poetry \
    POETRY_CACHE_DIR=/app/.cache \
    POETRY_VERSION=1.6.1

RUN python3 -m venv $POETRY_HOME \
    && $POETRY_HOME/bin/pip install poetry==${POETRY_VERSION} \
    && $POETRY_HOME/bin/poetry --version
ENV PATH="$POETRY_HOME/bin:$PATH"

ADD . /app

WORKDIR /app
RUN poetry install --without dev

ENTRYPOINT /app/entrypoint.sh
