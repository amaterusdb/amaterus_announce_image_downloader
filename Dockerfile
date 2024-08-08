# syntax=docker/dockerfile:1.9
ARG BASE_IMAGE=python:3.12

FROM ${BASE_IMAGE} AS poetry-export-stage

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:${PATH}

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install pipx

RUN --mount=type=cache,target=/root/.cache/pipx \
    pipx install poetry

RUN --mount=type=cache,target=/root/.cache/pypoetry/cache \
    --mount=type=cache,target=/root/.cache/pypoetry/artifacts \
    poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock /opt/poetry-export/

WORKDIR /opt/poetry-export
RUN poetry export --only main --output /opt/poetry-export/requirements.txt


FROM ${BASE_IMAGE} AS runtime-stage

ENV PYTHONUNBUFFERED=1

COPY --from=poetry-export-stage /opt/poetry-export/requirements.txt /opt/poetry-export/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /opt/poetry-export/requirements.txt

COPY ./pyproject.toml ./README.md /opt/amaterus_announce_image_downloader/
COPY ./amaterus_announce_image_downloader /opt/amaterus_announce_image_downloader/amaterus_announce_image_downloader

RUN python -m compileall /opt/amaterus_announce_image_downloader
RUN pip install --no-deps --editable /opt/amaterus_announce_image_downloader

USER "1000:1000"
ENTRYPOINT [ "python", "-m", "amaterus_announce_image_downloader" ]
