from bballer.scrapers.TeamScraper import TeamSeasonScraper


class TestTeamSeasonScraper:
    def test_roster_scrape(self):
        roster = TeamSeasonScraper("CLE", 2016).get_roster()
        for player in roster:
            assert isinstance(player["name"], str)
            assert isinstance(player["url"], str)
            assert isinstance(player["number"], int)
