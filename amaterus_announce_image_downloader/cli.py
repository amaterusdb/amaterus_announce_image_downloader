import os
from argparse import ArgumentParser
from pathlib import Path

from dotenv import load_dotenv


def crawl(
    amaterus_hasura_url: str,
    internal_useragent: str,
    external_useragent: str,
    output_dir: Path,
) -> None:
    # TODO: impl
    pass


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
