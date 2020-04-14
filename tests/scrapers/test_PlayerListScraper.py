from unittest.case import TestCase

from bballer.scrapers.PlayerListScraper import PlayerListScraper
from tests.scrapers.test_Scraper import get_resource


class TestPlayerListScraper(TestCase):

    def test_scrape(self):
        s = PlayerListScraper(get_resource("w.html"))
        urls = s.get_content()
        assert len(urls) == 364
        assert all([url.startswith("https://www.basketball-reference.com/players/") for url in urls])
