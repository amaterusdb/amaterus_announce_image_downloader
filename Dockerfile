# syntax=docker/dockerfile:1.6
FROM python:3.11

ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/user/.local/bin:${PATH}

RUN <<EOF
    set -eu

    apt-get update

    apt-get install -y \
        gosu

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

RUN <<EOF
    set -eu

    groupadd -o -g 1000 user
    useradd -m -o -u 1000 -g user user
EOF

ARG POETRY_VERSION=1.7.1
RUN <<EOF
    set -eu

    gosu user pip install "poetry==${POETRY_VERSION}"
EOF

ADD ./pyproject.toml ./poetry.lock /code/
RUN <<EOF
    set -eu

    cd /code
    gosu user poetry install --only main
EOF

ADD ./amaterus_announce_image_downloader /code/amaterus_announce_image_downloader

WORKDIR /code
ENTRYPOINT [ "gosu", "user", "poetry", "run", "python", "-m", "amaterus_announce_image_downloader" ]
