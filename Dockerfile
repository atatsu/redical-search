# --------------------------------------------------------------------
# Base stage for getting all the dependencies installed
# --------------------------------------------------------------------
FROM python:3.8-slim-buster as base
ENV PATH=/root/.poetry/bin:$PATH
WORKDIR /code
COPY pyproject.toml poetry.lock /code/
COPY ./lib/redical /code/lib/redical
RUN apt-get update \
	&& apt-get install build-essential curl -y \
	&& curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - \
	&& poetry config virtualenvs.create false \
	&& poetry install --no-dev --no-root;


# ----------------------------------------
# Build stage specifically for development
# ----------------------------------------
FROM base as dev
ENV PYTHONASYNCIODEBUG=1
RUN poetry install --no-root
COPY . .
RUN script/cleanup \
	&& poetry install;
