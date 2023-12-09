# amaterus_announce_image_downloader

## Usage

```shell
poetry install

poetry run python -m amaterus_announce_image_downloader twitter_tweet_image --output_dir "work/twitter_tweet_images/"

poetry run python -m amaterus_announce_image_downloader youtube_live_thumbnail_image --output_dir "work/youtube_live_thumbnail_images/"

poetry run python -m amaterus_announce_image_downloader youtube_video_thumbnail_image --output_dir "work/youtube_video_thumbnail_images/"
```

### Docker usage

```shell
mkdir -p "./work"
sudo chown -R "1000:1000" "./work"

sudo docker build -t docker.aoirint.com/aoirint/amaterus_announce_image_downloader .
sudo docker run --rm --env-file ./.env -v "./work:/code/work" docker.aoirint.com/aoirint/amaterus_announce_image_downloader
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
