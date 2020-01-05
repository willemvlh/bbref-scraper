from typing import List, Tuple
from Scraper import Scraper, PlayerPageScraper


class _SearchPageScraper(Scraper):
    def get_player_results(self) -> List[Tuple]:
        if self._parsed.find("div", id="info"):
            # sometimes the search automatically redirects to a specific player page.
            redirected_url = self._parsed.find("link", rel="canonical").attrs["href"]
            name = self._parsed.find("h1", itemprop="name").text
            return [(name, redirected_url)]
        results = []
        for result in self._parsed.find("div", id="players").find_all("div", class_="search-item"):
            name = result.find("div", class_="search-item-name").find("a")
            results.append((name.string, "https://www.basketball-reference.com" + name.attrs["href"]))
        return results


class Search:
    @staticmethod
    def search(name: str) -> List[Tuple]:
        scraper = _SearchPageScraper(
            f"https://www.basketball-reference.com/search/search.fcgi?search={name}")
        return scraper.get_player_results()
