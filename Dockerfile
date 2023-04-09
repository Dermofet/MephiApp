FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /api/

RUN apt-get update && apt-get install -y libgl1-mesa-dev && apt-get -y install cron

ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.2.0 \
    POETRY_VIRTUALENVS_CREATE=false

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$PATH:$POETRY_HOME/bin"

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* /api/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

RUN echo "*/01 * * * * python3 /api/parsing/news/run_parsing_new_news.py >> /api/cronlogs.log 2>&1" >> /etc/crontab

COPY . /api/

ENV PYTHONPATH ".."

CMD ["bash", "./entrypoint.sh"]