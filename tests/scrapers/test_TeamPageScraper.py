from bballer.scrapers.TeamScraper import TeamPageScraper
from tests.scrapers.test_Scraper import get_resource


class TestTeamPageScraper:

    def test_team(self):
        scr = TeamPageScraper("CLE")
        team = scr.team()
        assert team.name == "Cleveland Cavaliers"
        assert team.code == "CLE"

    def test_team_with_url(self):
        team = TeamPageScraper(get_resource("cavs.html")).team()
        assert team.name == "Cleveland Cavaliers"
        assert team.wins == 1858
        assert team.losses == 2149
        assert team.playoff_appearances == 22
        assert team.championships == 1
        assert team.code == "CLE"
        assert len(team.seasons) == 50

    def test_roster(self):
        team = TeamPageScraper(get_resource("cavs.html")).team()
        s = team.seasons[-1]
        assert len(s.roster) > 10

    def test_season(self):
        team = TeamPageScraper(get_resource("cavs.html")).team()
        last_season = team.seasons[-1]
        assert last_season.losses == 27
        assert last_season.wins == 10
        assert last_season.pace == 98.8
        assert last_season.rel_pace == -1.6
        assert last_season.ortg == 105.6
        assert last_season.rel_ortg == -3.6
        assert last_season.season == "2019-20"
        assert not last_season.won_championship
        assert not last_season.made_playoffs
        team = TeamPageScraper(get_resource("cavs.html")).team()
        championship_season = team.season("2015-16")
        assert championship_season.wins == 57
        assert championship_season.won_championship
        assert championship_season.made_playoffs
