import os
import time
import traceback
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel

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


def crawl(
    amaterus_hasura_url: str,
    internal_useragent: str,
    external_useragent: str,
    output_dir: Path,
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


def main() -> None:
    load_dotenv()

    ENV_APP_AMATERUS_HASURA_URL = os.environ.get("APP_AMATERUS_HASURA_URL") or None
    ENV_APP_INTERNAL_USERAGENT = os.environ.get("APP_INTERNAL_USERAGENT") or None
    ENV_APP_EXTERNAL_USERAGENT = os.environ.get("APP_EXTERNAL_USERAGENT") or None
    ENV_APP_OUTPUT_DIR = os.environ.get("APP_OUTPUT_DIR") or None

    parser = ArgumentParser()
    parser.add_argument(
        "--amaterus_hasura_url",
        type=str,
        default=ENV_APP_AMATERUS_HASURA_URL,
        required=ENV_APP_AMATERUS_HASURA_URL is None,
        help="Amaterus Hasura URL",
    )
    parser.add_argument(
        "--internal_useragent",
        type=str,
        default=ENV_APP_INTERNAL_USERAGENT,
        required=ENV_APP_INTERNAL_USERAGENT is None,
        help="Useragent for internal HTTP request (Amaterus Hasura)",
    )
    parser.add_argument(
        "--external_useragent",
        type=str,
        default=ENV_APP_EXTERNAL_USERAGENT,
        required=ENV_APP_EXTERNAL_USERAGENT is None,
        help="Useragent for external HTTP request (Twitter)",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=ENV_APP_OUTPUT_DIR,
        required=ENV_APP_OUTPUT_DIR is None,
        help="Output directory",
    )
    args = parser.parse_args()

    amaterus_hasura_url: str = args.amaterus_hasura_url
    internal_useragent: str = args.internal_useragent
    external_useragent: str = args.external_useragent
    output_dir: Path = args.output_dir

    crawl(
        amaterus_hasura_url=amaterus_hasura_url,
        internal_useragent=internal_useragent,
        external_useragent=external_useragent,
        output_dir=output_dir,
    )
