from datetime import date

from bballer.models.game import Game, CondensedGamelog
from bballer.scrapers.GameLogScraper import GameLogScraper
from bballer.scrapers.GameScraper import GameScraper


class TestGameScraper:
    def test_game_scraper(self):
        url = "https://www.basketball-reference.com/boxscores/201611010CLE.html"
        scr = GameScraper(url)
        game = scr.get_content()
        assert game.home_team == "Cleveland Cavaliers"
        assert game.away_team == "Houston Rockets"
        assert game.score == (120, 128)
        assert game.date.day == 1
        assert game.date.month == 11
        assert game.date.year == 2016
        assert game.score_by_quarter == [(35, 29), (24, 34), (25, 22), (36, 43)]
        assert len(game.statlines) == 2
        assert len(list(statline for team_statlines in game.statlines for statline in team_statlines)) == 26
        harden_statline: CondensedGamelog = [sl for sl in game.statlines[0] if sl.player_id == "hardeja01"][0]
        assert harden_statline.seconds_played == 2290
        assert harden_statline.fg_made == 13
        assert harden_statline.fg_attempted == 20
        assert harden_statline.three_fg_made == 5
        assert harden_statline.three_fg_attempted == 9
        assert harden_statline.ft_made == 10
        assert harden_statline.ft_attempted == 14
        assert harden_statline.offensive_rebounds == 1
        assert harden_statline.defensive_rebounds == 6
        assert harden_statline.assists == 15
        assert harden_statline.steals == 1
        assert harden_statline.fouls == 3
        assert harden_statline.points == 41
        assert harden_statline.plus_minus == 10
        assert harden_statline.played
        assert harden_statline.started


class TestGameLogScraper:

    def test_rebounds(self):
        from bballer import player
        pl = player.get_by_name("DJ Mbenga")
        s = pl.seasons[1]
        for r in [gl.rebounds for gl in s.game_logs()]:
            assert r is None or isinstance(r, int)

    def test_scrape(self):
        url = "https://www.basketball-reference.com/players/m/mbengdj01/gamelog/2008/"
        scr = GameLogScraper(url)
        logs = list(scr._get_game_logs())
        assert len(logs) == 70
        first_game = logs[0]
        assert not first_game.played
        assert first_game.team == "GSW"
        assert first_game.opponent == "TOR"
        assert first_game.date == date.fromisoformat("2007-11-18")
        assert first_game.points is None

        second_game = logs[1]
        assert not second_game.started
        assert second_game.played
        assert second_game.team == "GSW"
        assert second_game.opponent == "NYK"
        assert second_game.result == "W (+26)"
        assert second_game.seconds_played == 597
        assert second_game.fg_made == 1
        assert second_game.fg_attempted == 3
        assert second_game.three_fg_made == 0
        assert second_game.three_fg_attempted == 0
        assert second_game.ft_made == 0
        assert second_game.ft_attempted == 0
        assert second_game.offensive_rebounds == 1
        assert second_game.defensive_rebounds == 0
        assert second_game.assists == 0
        assert second_game.steals == 0
        assert second_game.blocks == 1
        assert second_game.turnovers == 0
        assert second_game.fouls == 3
        assert second_game.points == 2
        assert second_game.game_score == 0.5
        assert second_game.plus_minus == 1

        assert isinstance(second_game.to_game(), Game)
