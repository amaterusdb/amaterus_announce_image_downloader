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


class TwitterTweetImage(BaseModel):
    id: str
    url: str


class FetchTwitterTweetImageResponseData(BaseModel):
    twitter_tweet_images: list[TwitterTweetImage]


class FetchTwitterTweetImageResponse(BaseModel):
    data: FetchTwitterTweetImageResponseData


def fetch_twitter_tweet_images(
    amaterus_hasura_url: str,
    internal_useragent: str,
) -> list[TwitterTweetImage]:
    amaterus_hasura_api_url = urljoin(amaterus_hasura_url, "v1/graphql")

    query = """
query GetTwitterTweetImages {
  twitter_tweet_images {
    id
    url
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

    response = FetchTwitterTweetImageResponse.model_validate(raw_response.json())
    return response.data.twitter_tweet_images


class TwitterTweetImageMetadata(BaseModel):
    id: str
    url: str
    content_type: str
    file_name: str
    fetched_at: datetime


def crawl_twitter_tweet_images(
    amaterus_hasura_url: str,
    internal_useragent: str,
    external_useragent: str,
    output_dir: Path,
    logger: Logger,
) -> None:
    twitter_tweet_images = fetch_twitter_tweet_images(
        amaterus_hasura_url=amaterus_hasura_url,
        internal_useragent=internal_useragent,
    )

    interval_after_request: float = 10

    for twitter_tweet_image in twitter_tweet_images:
        metadata_file = output_dir / f"{twitter_tweet_image.id}.json"
        if metadata_file.exists():
            # already fetched
            continue

        error_metadata_file = output_dir / f"{twitter_tweet_image.id}.error.txt"
        if error_metadata_file.exists():
            # errored
            continue

        fetched_at = datetime.now().astimezone(tz=JST)

        try:
            logger.info(
                f"[id={twitter_tweet_image.id}] Send request to {twitter_tweet_image.url}"
            )
            res = httpx.get(
                url=twitter_tweet_image.url,
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

        file_name = f"{twitter_tweet_image.id}{suffix}"

        output_file = output_dir / file_name
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(res.content)

        metadata_file.write_text(
            TwitterTweetImageMetadata(
                id=twitter_tweet_image.id,
                url=twitter_tweet_image.url,
                content_type=content_type,
                file_name=file_name,
                fetched_at=fetched_at,
            ).model_dump_json(),
            encoding="utf-8",
        )

        time.sleep(interval_after_request)


def twitter_tweet_image_command(
    args: Namespace,
    logger: Logger,
) -> None:
    amaterus_hasura_url: str = args.amaterus_hasura_url
    internal_useragent: str = args.internal_useragent
    external_useragent: str = args.external_useragent
    output_dir: Path = args.output_dir

    crawl_twitter_tweet_images(
        amaterus_hasura_url=amaterus_hasura_url,
        internal_useragent=internal_useragent,
        external_useragent=external_useragent,
        output_dir=output_dir,
        logger=logger,
    )


def add_twitter_tweet_image_arguments(
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
        help="Useragent for external HTTP request (Twitter)",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        required=True,
        help="Output directory",
    )
    parser.set_defaults(
        handler=twitter_tweet_image_command,
    )
