import logging

from bballer.scrapers.misc import BulkScraper
from tests.scrapers.test_Scraper import get_resource


class TestBulkScraper:

    def test_scrape(self):
        logging.getLogger().setLevel(logging.DEBUG)
        bulk_scr = BulkScraper(map(get_resource, ["lebron_james.html", "carmelo_anthony.html"]))
        processed = list(bulk_scr.scrape_all())
        assert len(processed) == 2
        assert "Carmelo Anthony" in [p.name for p in processed]

    def test_double_scrape(self):
        bulk_scr = BulkScraper(map(get_resource, ["lebron_james.html", "lebron_james.html"]))
        players = list(bulk_scr.scrape_all())
        assert len(players) == 1
