import logging
from functools import lru_cache

import requests


@lru_cache(maxsize=100)
def download(url: str):
    logging.debug(f"Connecting to {url}")
    r = requests.get(url)
    r.raise_for_status()
    return r.content
