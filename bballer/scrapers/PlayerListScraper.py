from bballer.scrapers.base import Scraper


class PlayerListScraper(Scraper):
    def __init__(self, url: str):
        super().__init__(url)

    def get_player_urls(self):
        cells = self._parsed.find_all("th", {"data-stat": "player", "scope": "row"})
        return ["https://www.basketball-reference.com" + cell.find_next("a").attrs["href"] for cell in cells]