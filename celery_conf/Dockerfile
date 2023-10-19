FROM python:3.9

WORKDIR /mephiapp-celery/

RUN apt-get update && apt-get install -y libgl1-mesa-dev

ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.2.0 \
    POETRY_VIRTUALENVS_CREATE=false

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$PATH:$POETRY_HOME/bin"

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ../pyproject.toml poetry.lock* /mephiapp-celery/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=False
RUN bash -c "if [ $INSTALL_DEV = True ] ; then poetry install --no-root ; else poetry install --no-root --without dev ; fi"

COPY .env /mephiapp-celery/.env

CMD ["celery", "--app", "celery_conf.beat.beat_app", "beat", "--loglevel=debug"]