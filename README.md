# amaterus_announce_image_downloader

## Usage

```shell
poetry install

poetry run python -m amaterus_announce_image_downloader
```

### Docker usage

```shell
sudo docker build -t amaterus_announce_image_downloader .
sudo docker run --rm -env-file ./.env amaterus_announce_image_downloader
```

## Dependency management

```shell
poetry install

poetry add httpx
poetry add --group dev pytest
```

## Code format

```shell
poetry run pysen run lint
poetry run pysen run format
```
