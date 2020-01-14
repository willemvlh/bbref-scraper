from typing import List, Tuple

from bballer.scrapers.base import Scraper


class _SearchPageScraper(Scraper):
    def get_search_results(self, table_id) -> List[Tuple]:
        import requests
        requests.get
        if self._parsed.find("div", id="info"):
            # sometimes the search automatically redirects to a specific player page.
            redirected_url = self._parsed.find("link", rel="canonical").attrs["href"]
            name = self._parsed.find("h1", itemprop="name").text
            return [(name, redirected_url)]
        results = []
        for result in self._parsed.find("div", id=table_id).find_all("div", class_="search-item"):
            name = result.find("div", class_="search-item-name").find("a")
            results.append((name.string.strip(), "https://www.basketball-reference.com" + name.attrs["href"]))
        return results


class Search:

    @classmethod
    def _new_scraper(cls, search_item):
        return _SearchPageScraper(
            f"https://www.basketball-reference.com/search/search.fcgi?search={search_item}")

    @classmethod
    def search_players(cls, name: str) -> List[Tuple]:
        return cls._new_scraper(name).get_search_results("players")

    @classmethod
    def search_teams(cls, name: str) -> List[Tuple]:
        return cls._new_scraper(name).get_search_results("teams")
