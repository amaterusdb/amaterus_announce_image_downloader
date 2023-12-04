# amaterus_announce_image_downloader

## Usage

```shell
poetry install

poetry run python -m amaterus_announce_image_downloader
```

### Docker usage

```shell
mkdir -p "./work"
sudo chown -R "1000:1000" "./work"

sudo docker build -t amaterus_announce_image_downloader .
sudo docker run --rm --env-file ./.env -v "./work:/code/amaterus_announce_image_downloader/work" amaterus_announce_image_downloader
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
