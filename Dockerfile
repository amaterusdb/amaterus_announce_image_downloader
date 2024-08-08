# syntax=docker/dockerfile:1.9
ARG BASE_IMAGE=python:3.11

FROM ${BASE_IMAGE} AS poetry-export-stage

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:${PATH}

ARG PIPX_VERSION=1.6.0
RUN --mount=type=cache,target=/root/.cache/pip <<EOF
    set -eu

    pip install "pipx==${PIPX_VERSION}"
EOF

ARG POETRY_VERSION=1.8.3
RUN --mount=type=cache,target=/root/.cache/pipx <<EOF
    set -eu

    pipx install "poetry==${POETRY_VERSION}"
EOF

RUN --mount=type=cache,target=/root/.cache/pypoetry/cache \
    --mount=type=cache,target=/root/.cache/pypoetry/artifacts <<EOF
    set -eu

    poetry self add poetry-plugin-export
EOF

COPY ./pyproject.toml ./poetry.lock /opt/poetry-export/

WORKDIR /opt/poetry-export
RUN poetry export --only main --output /opt/poetry-export/requirements.txt


FROM ${BASE_IMAGE} AS runtime-stage

ENV PYTHONUNBUFFERED=1

COPY --from=poetry-export-stage /opt/poetry-export /opt/poetry-export

RUN python -m venv /opt/python
ENV PATH=/opt/python/bin:${PATH}

RUN --mount=type=cache,target=/root/.cache/pip pip install -r /opt/poetry-export/requirements.txt

COPY ./pyproject.toml ./README.md /opt/amaterus_announce_image_downloader/
COPY ./amaterus_announce_image_downloader /opt/amaterus_announce_image_downloader/amaterus_announce_image_downloader

RUN python -m compileall /opt/amaterus_announce_image_downloader
RUN pip install --no-deps --editable /opt/amaterus_announce_image_downloader

USER "1000:1000"
ENTRYPOINT [ "python", "-m", "amaterus_announce_image_downloader" ]
