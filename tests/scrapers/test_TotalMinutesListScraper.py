from bballer.scrapers.misc import TotalMinutesScraper


class TestTotalMinutesListScraper:
    def test_scrape(self):
        s = TotalMinutesScraper(2000)
        urls = s.get_player_urls()
        assert len(urls) > 10
        assert all([url.startswith("https://www.basketball-reference.com/players/") for url in urls])
