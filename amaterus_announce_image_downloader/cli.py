import logging
from argparse import ArgumentParser
from logging import getLogger

from dotenv import load_dotenv

from . import __VERSION__ as APP_VERSION
from .app_config import load_app_config_from_env
from .twitter_tweet_image_cli import add_twitter_tweet_image_arguments
from .youtube_live_thumbnail_image_cli import add_youtube_live_thumbnail_image_arguments
from .youtube_video_thumbnail_image_cli import (
    add_youtube_video_thumbnail_image_arguments,
)


def main() -> None:
    load_dotenv()

    app_config = load_app_config_from_env()

    parser = ArgumentParser()
    parser.add_argument(
        "--version",
        action="version",
        version=APP_VERSION,
    )

    subparsers = parser.add_subparsers()

    subparser_twitter_tweet_image = subparsers.add_parser("twitter_tweet_image")
    add_twitter_tweet_image_arguments(
        parser=subparser_twitter_tweet_image,
        app_config=app_config,
    )

    subparser_youtube_live_thumbnail_image = subparsers.add_parser(
        "youtube_live_thumbnail_image"
    )
    add_youtube_live_thumbnail_image_arguments(
        parser=subparser_youtube_live_thumbnail_image,
        app_config=app_config,
    )

    subparser_youtube_video_thumbnail_image = subparsers.add_parser(
        "youtube_video_thumbnail_image"
    )
    add_youtube_video_thumbnail_image_arguments(
        parser=subparser_youtube_video_thumbnail_image,
        app_config=app_config,
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
    )
    logger = getLogger()

    if hasattr(args, "handler"):
        args.handler(args, logger)
    else:
        parser.print_help()
