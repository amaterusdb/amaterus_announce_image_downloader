import time
import traceback
from argparse import ArgumentParser, Namespace
from datetime import datetime
from logging import Logger
from pathlib import Path
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import httpx
from pydantic import BaseModel

from .app_config import AppConfig

JST = ZoneInfo("Asia/Tokyo")


class YoutubeLive(BaseModel):
    id: str
    remote_youtube_video_id: str


class FetchYoutubeLiveResponseData(BaseModel):
    youtube_lives: list[YoutubeLive]


class FetchYoutubeLivesResponse(BaseModel):
    data: FetchYoutubeLiveResponseData


def fetch_youtube_live_thumbnail_images(
    amaterus_hasura_url: str,
    internal_useragent: str,
) -> list[YoutubeLive]:
    amaterus_hasura_api_url = urljoin(amaterus_hasura_url, "v1/graphql")

    query = """
query GetYoutubeLives {
  youtube_lives {
    id
    remote_youtube_video_id
  }
}
"""

    raw_response = httpx.post(
        url=amaterus_hasura_api_url,
        headers={
            "User-Agent": internal_useragent,
        },
        json={
            "query": query,
        },
        timeout=15,
    )
    raw_response.raise_for_status()

    response = FetchYoutubeLivesResponse.model_validate(raw_response.json())
    return response.data.youtube_lives


class YoutubeLiveThumbnailImageMetadata(BaseModel):
    id: str
    url: str
    content_type: str
    file_name: str
    fetched_at: datetime


def crawl_youtube_live_thumbnail_images(
    amaterus_hasura_url: str,
    internal_useragent: str,
    external_useragent: str,
    output_dir: Path,
    logger: Logger,
) -> None:
    youtube_lives = fetch_youtube_live_thumbnail_images(
        amaterus_hasura_url=amaterus_hasura_url,
        internal_useragent=internal_useragent,
    )

    interval_after_request: float = 10

    for youtube_live in youtube_lives:
        metadata_file = output_dir / f"{youtube_live.id}.json"
        if metadata_file.exists():
            # already fetched
            continue

        error_metadata_file = output_dir / f"{youtube_live.id}.error.txt"
        if error_metadata_file.exists():
            # errored
            continue

        fetched_at = datetime.now().astimezone(tz=JST)

        try:
            thumbnail_image_url = (
                f"https://i.ytimg.com/vi/{youtube_live.remote_youtube_video_id}/"
                "maxresdefault.jpg"
            )

            logger.info(f"[id={youtube_live.id}] Send request to {thumbnail_image_url}")
            res = httpx.get(
                url=thumbnail_image_url,
                headers={
                    "User-Agent": external_useragent,
                },
                timeout=15,
            )
            res.raise_for_status()
        except httpx.HTTPError:
            error_metadata_file.parent.mkdir(parents=True, exist_ok=True)
            error_metadata_file.write_text(
                traceback.format_exc() + "\n",
                encoding="utf-8",
            )
            time.sleep(interval_after_request)
            continue

        content_type = res.headers.get("Content-Type")
        if content_type is None:
            error_metadata_file.parent.mkdir(parents=True, exist_ok=True)
            error_metadata_file.write_text(
                "Response header Content-Type cannot be None\n",
                encoding="utf-8",
            )
            time.sleep(interval_after_request)
            continue

        suffix: str | None = None
        if content_type == "image/jpeg":
            suffix = ".jpg"
        elif content_type == "image/png":
            suffix = ".png"

        if suffix is None:
            error_metadata_file.parent.mkdir(parents=True, exist_ok=True)
            error_metadata_file.write_text(
                f"Unsupported Content-Type: {content_type}\n",
                encoding="utf-8",
            )
            time.sleep(interval_after_request)
            continue

        file_name = f"{youtube_live.id}{suffix}"

        output_file = output_dir / file_name
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(res.content)

        metadata_file.write_text(
            YoutubeLiveThumbnailImageMetadata(
                id=youtube_live.id,
                url=thumbnail_image_url,
                content_type=content_type,
                file_name=file_name,
                fetched_at=fetched_at,
            ).model_dump_json(),
            encoding="utf-8",
        )

        time.sleep(interval_after_request)


def youtube_live_thumbnail_image_command(
    args: Namespace,
    logger: Logger,
) -> None:
    amaterus_hasura_url: str = args.amaterus_hasura_url
    internal_useragent: str = args.internal_useragent
    external_useragent: str = args.external_useragent
    output_dir: Path = args.output_dir

    crawl_youtube_live_thumbnail_images(
        amaterus_hasura_url=amaterus_hasura_url,
        internal_useragent=internal_useragent,
        external_useragent=external_useragent,
        output_dir=output_dir,
        logger=logger,
    )


def add_youtube_live_thumbnail_image_arguments(
    parser: ArgumentParser,
    app_config: AppConfig,
) -> None:
    parser.add_argument(
        "--amaterus_hasura_url",
        type=str,
        default=app_config.amaterus_hasura_url,
        required=app_config.amaterus_hasura_url is None,
        help="Amaterus Hasura URL",
    )
    parser.add_argument(
        "--internal_useragent",
        type=str,
        default=app_config.internal_useragent,
        required=app_config.internal_useragent is None,
        help="Useragent for internal HTTP request (Amaterus Hasura)",
    )
    parser.add_argument(
        "--external_useragent",
        type=str,
        default=app_config.external_useragent,
        required=app_config.external_useragent is None,
        help="Useragent for external HTTP request (YouTube)",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        required=True,
        help="Output directory",
    )
    parser.set_defaults(
        handler=youtube_live_thumbnail_image_command,
    )
