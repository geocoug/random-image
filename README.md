# random-image

[![Docker](https://github.com/geocoug/random-image/workflows/docker%20build/badge.svg)](https://github.com/geocoug/random-image/actions/workflows/docker-build.yml)

Download a random [Unsplash](https://unsplash.com/) image.

## Usage

### CLI

```sh
usage: random_image.py [-h] [-v] tracker_json output_dir

Download a random Unsplash image.

positional arguments:
  tracker_json   JSON file to track requests.
  output_dir     Directory to save image.

options:
  -h, --help     show this help message and exit
  -v, --verbose  Control the amount of information to display.
```

### Docker

#### Build the Image

```sh
docker build -t random_image .
```

#### Run

```sh
docker run -it --rm -v $(pwd):/usr/local/app random_image
```
