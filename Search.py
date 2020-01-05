from typing import List, Tuple
from Scraper import Scraper


class _SearchPageScraper(Scraper):
    def get_player_results(self):
        results = []
        for result in self._parsed.find("div", id="players").find_all("div", class_="search-item"):
            name = result.find("div", class_="search-item-name").find("a")
            results.append((name.string, "https://www.basketball-reference.com" + name.attrs["href"]))
        return results


class Search:
    @staticmethod
    def search(name: str) -> List[Tuple]:
        scraper = _SearchPageScraper(
            f"https://www.basketball-reference.com/search/search.fcgi?hint=&search={name}&pid=&idx=")
        return scraper.get_player_results()
