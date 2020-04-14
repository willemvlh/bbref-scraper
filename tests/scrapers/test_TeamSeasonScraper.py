from bballer.models.PlayerShell import PlayerShell
from bballer.scrapers.TeamScraper import TeamSeasonScraper


class TestTeamSeasonScraper:
    def test_roster_scrape(self):
        roster = TeamSeasonScraper("CLE", 2016).get_roster()
        assert all([isinstance(player, PlayerShell) for player in roster])
        assert all([player.name for player in roster])
        assert all([player.url and player.url.startswith("http") for player in roster])
        assert all([isinstance(player.number, int) for player in roster])
