from bballer.scrapers.base import Scraper
from tests.scrapers.utils import get_resource


class TestBaseScraper():

    def test_get_commented_table_with_id(self):
        scr = Scraper(get_resource("lebron_james.html"))
        table = scr.get_commented_table_with_id("contracts_.*")
        assert table["id"] == "contracts_lal"
