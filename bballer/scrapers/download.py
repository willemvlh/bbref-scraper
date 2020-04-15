import logging
import time
from datetime import datetime
from functools import lru_cache
from threading import Lock

import requests

CACHE_SIZE = 100
SLEEP_PERIOD_SECS = 0.1


class Download:
    last_download_start_timestamp: float = None
    # Indicates the time a download was last started.
    last_set_by: str = None
    lock = Lock()

    @classmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def download(cls, url: str):
        with cls.lock:
            # We introduce a small thread-safe delay between the start of each request to give basketball-reference some
            # breathing room.
            ts = datetime.now().timestamp()
            if cls.last_download_start_timestamp:
                diff = ts - cls.last_download_start_timestamp
                logging.debug(f"Difference is {diff}s")
                logging.debug(f"Lock last set by {cls.last_set_by}")
                if diff < SLEEP_PERIOD_SECS:
                    sleep = SLEEP_PERIOD_SECS - diff
                    logging.debug(f"Waiting for {sleep}s")
                    time.sleep(sleep)
                else:
                    logging.debug("Not waiting...")
        logging.debug(f"Connecting to {url}")
        cls.last_download_start_timestamp = datetime.now().timestamp()
        cls.last_set_by = url
        r = requests.get(url)
        logging.debug(f"Downloaded in {datetime.now().timestamp() - cls.last_download_start_timestamp}")
        r.raise_for_status()
        return r.content
