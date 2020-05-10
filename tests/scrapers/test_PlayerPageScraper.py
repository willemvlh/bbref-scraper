from collections.abc import Generator
from datetime import date

from bballer.models.gamelog import GameLog
from bballer.models.player import DraftPick
from bballer.models.stats import StatLine
from bballer.scrapers.PlayerPageScraper import PlayerPageScraper
from tests.scrapers.utils import get_resource


class TestPlayerPageScraper:
    lebron_james = PlayerPageScraper(get_resource("lebron_james.html")).get_content()
    carmelo_anthony = PlayerPageScraper(get_resource("carmelo_anthony.html")).get_content()
    julius_erving = PlayerPageScraper(get_resource("julius_erving.html")).get_content()
    wilt_chamberlain = PlayerPageScraper(get_resource("chamberlain.html")).get_content()

    def test_equality(self):
        assert (self.carmelo_anthony != self.lebron_james)
        _set = {self.carmelo_anthony, self.carmelo_anthony}
        assert len(_set) == 1

    def test_name(self):
        assert self.carmelo_anthony.name == "Carmelo Anthony"

    def test_get_dob(self):
        dob = self.carmelo_anthony.date_of_birth
        assert isinstance(dob, date)
        assert dob == date(1984, 5, 29)

    def test_get_career_stats(self):
        stats = self.carmelo_anthony.career_stats
        assert isinstance(stats, StatLine)
        assert int(stats.games_started) > 1000

    def test_get_id(self):
        assert self.carmelo_anthony.id == "carmelo_anthony"

    def test_get_shooting_hand(self):
        assert self.carmelo_anthony.shooting_hand == "Right"

    def test_get_college(self):
        assert self.carmelo_anthony.college == "Syracuse"
        assert self.lebron_james.college is None

    def test_player(self):
        player = self.carmelo_anthony
        assert player.height_cm == 203
        assert player.height_in == 80
        assert player.weight_kg == 109
        assert player.weight_lb == 240
        seasons = list(player.seasons)
        assert len(seasons) > 10

    def test_seasons(self):
        erving = PlayerPageScraper(get_resource("julius_erving.html")).get_content()
        assert len(list(erving.seasons)) == 11  # ABA seasons must be discarded

    def test_game_log(self):
        # can't store this page locally because we depend on a hyperlink inside
        seasons = list(PlayerPageScraper(
            "https://www.basketball-reference.com/players/m/mbengdj01.html").get_content().seasons)
        gl = seasons[0].game_logs()
        assert len([game for game in gl if game.played]) == seasons[0].games_played

    def test_all_star(self):
        erving = PlayerPageScraper(get_resource("julius_erving.html")).get_content()
        assert len([season for season in list(self.julius_erving.seasons) if season.all_star]) == 11

    def test_get_playoff_totals(self):
        playoffs = list(self.julius_erving.playoffs)
        assert len(playoffs) == 11
        assert sum([season.points for season in playoffs]) == 3088

    def test_historical_player(self):
        player = PlayerPageScraper(get_resource("tom_hawkins.html")).get_content()
        assert player.name == "Tom Hawkins"
        assert player.date_of_birth == date(1936, 12, 22)

    def test_salaries(self):
        anthony = self.carmelo_anthony
        assert len(anthony.salaries) == 17
        assert all([sal.amount > 0 for sal in anthony.salaries])
        assert all([sal.team and sal.team.startswith("http") for sal in anthony.salaries])
        assert all([sal.season for sal in anthony.salaries])
        assert sum([sal.amount for sal in anthony.salaries]) > 200000000

    def test_salaries_none(self):
        assert self.wilt_chamberlain.salaries == []

    def test_draft_pick(self):
        dp = self.lebron_james.draft_pick
        assert isinstance(dp, DraftPick)
        assert dp.pick == 1
        assert dp.round == 1
        assert dp.overall == 1
        assert dp.team.name == "Cleveland Cavaliers"
        assert dp.team.url == "https://www.basketball-reference.com/teams/CLE"
        assert dp.year == 2003

    def test_seasons_and_playoffs_are_generators(self):
        assert isinstance(self.lebron_james.seasons, Generator)
        assert isinstance(self.lebron_james.playoffs, Generator)

    def test_contract(self):
        james = self.lebron_james
        assert james.contract
        assert len(james.contract.years) == 3
        assert all([year.season for year in james.contract.years])
        assert all([year.amount for year in james.contract.years])

        first_year = james.contract.years[0]
        assert first_year.season == "2019-20"
        assert first_year.amount == 37436858
        assert first_year.option is None

        third_year = james.contract.years[2]
        assert third_year.season == "2021-22"
        assert third_year.amount == 41002273
        # assert third_year.option == "Player"

        chamberlain = self.wilt_chamberlain
        assert not chamberlain.contract

        shayok = PlayerPageScraper(get_resource("shayok.html")).get_content()
        assert not shayok.contract

        simons = PlayerPageScraper(get_resource("anfernee_simons.html")).get_content()
        assert simons.contract.years[0].option == "player"
        assert simons.contract.years[1].option == "early termination"
        assert simons.contract.years[2].option == "team"

    def test_playoff_games(self):
        lbj = PlayerPageScraper("https://www.basketball-reference.com/players/j/jamesle01.html").get_content()
        po = next(lbj.playoffs)
        assert po.points == 400
        games = list(po.game_logs())
        assert len(games) == 13
        game: GameLog = games[0]
        assert game.date == date(2006, 4, 22)
        assert game.points == 32
        assert game.assists == 11
