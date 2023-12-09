import os
from pathlib import Path

from pydantic import BaseModel


class AppConfig(BaseModel):
    amaterus_hasura_url: str | None
    internal_useragent: str | None
    external_useragent: str | None
    output_dir: Path | None


def load_app_config_from_env() -> AppConfig:
    amaterus_hasura_url = os.environ.get("APP_AMATERUS_HASURA_URL") or None
    internal_useragent = os.environ.get("APP_INTERNAL_USERAGENT") or None
    external_useragent = os.environ.get("APP_EXTERNAL_USERAGENT") or None
    output_dir_string = os.environ.get("APP_OUTPUT_DIR") or None

    output_dir: Path | None = None
    if output_dir_string is not None:
        output_dir = Path(output_dir_string)

    return AppConfig(
        amaterus_hasura_url=amaterus_hasura_url,
        internal_useragent=internal_useragent,
        external_useragent=external_useragent,
        output_dir=output_dir,
    )
