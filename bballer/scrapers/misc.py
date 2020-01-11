import concurrent.futures
from typing import List

import jsonpickle

from bballer.models.player import Player
from bballer.scrapers.base import Scraper
from bballer.scrapers.player import PlayerPageScraper


class TotalMinutesScraper(Scraper):
    def __init__(self, year: int):
        url = f"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html"
        super().__init__(url)

    def get_player_urls(self):
        cells = self._parsed.find_all("td", {"data-stat": "player"})
        return ["https://www.basketball-reference.com" + cell.find_next("a").attrs["href"] for cell in cells]


class BulkScraper:
    def __init__(self, urls):
        self._urls = urls
        self._processed = []

    def scrape_all(self, _max: int = None) -> List[Player]:
        urls = set(self._urls[0:_max] if _max else self._urls)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            players = executor.map(lambda u: PlayerPageScraper(u).player(), urls)
            return list(players)

    def serialize(self):
        jsonpickle.set_encoder_options(name="json", indent=1)
        return jsonpickle.encode(self._processed, unpicklable=False)