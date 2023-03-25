#!/usr/bin/env python
# random_image.py

import argparse
import datetime
import json
import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

load_dotenv()
__version__ = os.getenv("VERSION")
__vdate = os.getenv("VERSION_DATE")

ACCESS_KEY = os.getenv("ACCESS_KEY")
FORMAT = "jpg"
WIDTH = "3840"  # 4k
ORIENTATION = "landscape"
TOPICS = [
    dict(id="bo8jQKTaE0Y", title="Wallpapers"),
    dict(id="6sMVjTLSkeQ", title="Nature"),
    # dict(id="BJJMtteDJA4", title="Current events"),
    # dict(id="wnzpLxs0nQY", title="Act for nature"),
    # dict(id="9QVREH9A3DU", title="Entrepreneur"),
    # dict(id="CDwuwXJAbEw", title="3d renders"),
    # dict(id="iUIsnVtjB0Y", title="Textures & patterns"),
    # dict(id="qPYsDzvJOYc", title="Experimental"),
    # dict(id="rnSKDHwwYUk", title="Architecture"),
    # dict(id="aeu6rL-j6ew", title="Business & work"),
    # dict(id="S4MKLAsBB74", title="Fashion"),
    # dict(id="hmenvQhUmxM", title="Film"),
    # dict(id="xjPR4hlkBGA", title="Food & drink"),
    # dict(id="_hb-dl4Q-4U", title="Health & wellness"),
    # dict(id="towJZFskpGg", title="People"),
    # dict(id="R_Fyn-Gwtlw", title="Interiors"),
    # dict(id="xHxYTMHLgOc", title="Street photography"),
    # dict(id="Fzo3zuOHN6w", title="Travel"),
    # dict(id="Jpg6Kidl-Hk", title="Animals"),
    # dict(id="_8zFHuhRhyo", title="Spirituality"),
    # dict(id="bDo48cUhwnY", title="Arts & culture"),
    # dict(id="dijpbw99kQQ", title="History"),
    # dict(id="Bn-DjrcBrwo", title="Athletics"),
    # dict(id="c7USHrQ0Ljw", title="COVID-19"),
    # dict(id="M8jVbLbTRws", title="Architecture & interior")
]


class RequestTracker:
    """Track requests to the Unsplash API.

    Per guidelines, only 50 requests

    are allowed per hour for a demo application.
    """

    def __init__(self: "RequestTracker", tracker: str) -> None:
        self.tracker = tracker
        self.archive = os.path.join(os.path.dirname(__file__), "archive.json")
        self.exists = self.tracker_exists()
        self.requests = [Any]
        self.request_rate_window = 60 * 60  # 1 hour
        self.request_rate_limit = 50  # 50 requests
        self.end_window = datetime.datetime.now()
        self.start_window = self.end_window - datetime.timedelta(
            seconds=self.request_rate_window,
        )
        self.read()

    def __len__(self: "RequestTracker") -> int:
        if self.exists:
            return len(self.requests)
        return 0

    def timestamp(self: "RequestTracker") -> str:
        return datetime.datetime.now().replace(microsecond=0).isoformat()

    def str_to_iso(self: "RequestTracker", timestamp: str) -> datetime.datetime:
        return datetime.datetime.fromisoformat(timestamp).replace(microsecond=0)

    def tracker_exists(self: "RequestTracker") -> bool:
        if os.path.exists(self.tracker):
            return True
        return False

    def read(self: "RequestTracker") -> None:
        if self.exists:
            with open(self.tracker) as f:
                self.requests = json.load(f)
            self.remove_outdated_requests()

    def write(self: "RequestTracker") -> None:
        with open(self.tracker, "w") as f:
            json.dump(self.requests, f, indent=2)

    def write_archive(self: "RequestTracker", request: dict) -> None:
        if os.path.exists(self.archive):
            with open(self.archive, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(request)
        with open(self.archive, "w") as f:
            json.dump(data, f, indent=2)

    def add(self: "RequestTracker", timestamp: str, **kwargs: dict) -> None:
        self.read()
        if self.rate_limit_ok():
            logger.info(
                f"{self.str_to_iso(timestamp)} -- Request {len(self)} of {self.request_rate_limit}",  # noqa
            )
            for key in kwargs:
                logger.info(
                    f"  {key}{' '*((max(map(len, kwargs)) + 1)- len(key))}: {kwargs[key]}",  # noqa
                )
            self.requests.append(
                dict(
                    timestamp=timestamp,
                    **kwargs,
                ),
            )
            self.write()
            self.write_archive(
                dict(
                    timestamp=timestamp,
                    **kwargs,
                ),
            )
        else:
            self.rate_limit_exceeded()

    def remove_outdated_requests(self: "RequestTracker") -> None:
        for request in self.requests:
            timestamp = self.str_to_iso(request["timestamp"])
            if not (timestamp >= self.start_window and timestamp <= self.end_window):
                self.requests.remove(request)

    def rate_limit_ok(self: "RequestTracker") -> bool:
        if len(self.requests) < self.request_rate_limit:
            return True
        return False

    def rate_limit_exceeded(self: "RequestTracker") -> str:
        return f"""
            Request limit reached. Please try again later.
            Limit = {self.request_rate_limit}/{self.request_rate_window} seconds.
        """


def clparser() -> argparse.ArgumentParser:
    """Create a parser to handle input arguments and displaying.

    a script specific help message.
    """
    desc_msg = """Download a random Unsplash image.\nVersion {}, {}""".format(
        __version__,
        __vdate,
    )
    parser = argparse.ArgumentParser(description=desc_msg)
    parser.add_argument(
        "tracker_json",
        help="JSON file to track requests.",
    )
    parser.add_argument(
        "output_dir",
        help="Directory to save image.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Control the amount of information to display.",
    )
    return parser


def create_dirs(dir: str) -> None:
    """Create a directory if it does not already exist.

    Args:
        dir (str): Path.
    """
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except OSError:
            raise


def send_request(url: str) -> requests.Response:
    """Send an HTTP GET request.

    Args:
        url (str): Request endpoint.

    Raises:
        requests.RequestException: Response errors.

    Returns:
        requests.Response: HTTP response.
    """
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException:
        raise
    if not response.ok:
        raise requests.RequestException(
            f"Request returned status code {response.status_code}.\nRequest: {url}",
        )
    return response


def download_unsplash_image(tracker: RequestTracker, output_dir: str) -> None:
    """Download a random image from Unsplash.

    Args:
        tracker (RequestTracker): RequestTracker object.
        output_dir (str): Directory to save doanloaded image.
    """
    endpoint = "https://api.unsplash.com/photos/random"
    topic_ids = ",".join([topic["id"] for topic in TOPICS])
    topic_names = ",".join([topic["title"] for topic in TOPICS])
    request = f"{endpoint}?orientation={ORIENTATION}&topics={topic_ids}&client_id={ACCESS_KEY}"  # noqa
    response = send_request(request).json()
    image_url = f"{response['urls']['raw']}&w={WIDTH}&fm={FORMAT}"
    image_id = response["id"]
    username = response["user"]["username"]
    filename = f"{username}-{image_id}.{FORMAT}"
    filepath = os.path.join(output_dir, filename)
    tracker.add(
        timestamp=tracker.timestamp(),
        username=username,
        image_id=image_id,
        request_url=request,
        image_url=image_url,
        filename=filename,
        filepath=filepath,
        topics=topic_names,
        format=FORMAT,
        width=WIDTH,
        orientation=ORIENTATION,
    )
    create_dirs(output_dir)
    with open(filepath, "wb") as f:
        f.write(send_request(image_url).content)


def main() -> None:
    """Main function."""
    tracker = RequestTracker(tracker_json)
    if tracker.rate_limit_ok():
        download_unsplash_image(tracker, output_dir)
    else:
        logger.warn(tracker.rate_limit_exceeded())


if __name__ == "__main__":
    parser = clparser()
    args = parser.parse_args()
    if args.verbose:
        logger.addHandler(stream_handler)
    output_dir = args.output_dir
    tracker_json = args.tracker_json
    main()
