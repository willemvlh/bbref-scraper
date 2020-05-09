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
        rookie_season = seasons[0]
        assert rookie_season.position == "SF"
        assert rookie_season.season == 2004
        assert rookie_season.games_started == 82
        assert rookie_season.games_played == 82
        assert rookie_season.minutes_played == 2995
        assert rookie_season.fg_attempted == 1465
        assert rookie_season.fg_made == 624
        assert rookie_season.three_fg_made == 69
        assert rookie_season.three_fg_attempted == 214
        assert rookie_season.two_fg_attempted == 1251
        assert rookie_season.two_fg_made == 555
        assert rookie_season.effective_fg_percentage == 0.449
        assert rookie_season.ft_made == 408
        assert rookie_season.ft_attempted == 525
        assert rookie_season.offensive_rebounds == 183
        assert rookie_season.defensive_rebounds == 315
        assert rookie_season.rebounds == 498
        assert not rookie_season.all_star
        assert rookie_season.assists == 227
        assert rookie_season.blocks == 41
        assert rookie_season.turnovers == 247
        assert rookie_season.steals == 97
        assert rookie_season.fouls == 225
        assert rookie_season.points == 1725

    def test_advanced_stats(self):
        player = PlayerPageScraper(get_resource("carmelo_anthony.html")).get_content()
        s = list(player.seasons)[0]
        assert s.advanced.assist_percentage == 13.8
        assert s.advanced.player_efficiency_rating == 17.6
        assert s.advanced.true_shooting_percentage == 0.509
        assert s.advanced.three_fg_attempt_rate == 0.146
        assert s.advanced.ft_attempt_rate == 0.358
        assert s.advanced.offensive_rebound_percentage == 6.8
        assert s.advanced.defensive_rebound_percentage == 12.1
        assert s.advanced.total_rebound_percentage == 9.4
        assert s.advanced.steal_percentage == 1.7
        assert s.advanced.block_percentage == 1.0
        assert s.advanced.turnover_percentage == 12.7
        assert s.advanced.usage_percentage == 28.5
        assert s.advanced.offensive_win_shares == 3.7
        assert s.advanced.defensive_win_shares == 2.4
        assert s.advanced.win_shares == 6.1
        assert s.advanced.win_shares_per_48 == 0.098
        assert s.advanced.offensive_box_plus_minus == 1.2
        assert s.advanced.defensive_box_plus_minus == -1.2
        assert s.advanced.box_plus_minus == 0
        assert s.advanced.value_over_replacement_player == 1.6

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

    def test_shooting_data(self):
        lbj = PlayerPageScraper("https://www.basketball-reference.com/players/j/jamesle01.html").get_content()
        first_season = next(lbj.seasons)
        shooting_data = first_season.shooting_data
        assert shooting_data.heaves_made == 0
        assert shooting_data.heaves_attempted == 3
        assert shooting_data.corner_three_point_fgp == 0.323
        assert shooting_data.corner_three_point_fga == 0.286
        assert shooting_data.three_point_fga_assisted == 0.746
        assert shooting_data.dunks_made == 91
        assert shooting_data.dunks_fga == 0.064
        assert shooting_data.two_point_fga_assisted == 0.442
        assert shooting_data.fgp_by_distance
        assert shooting_data.fga_by_distance

        assert shooting_data.fga_by_distance.two_point == 0.855
        assert shooting_data.fga_by_distance.zero_three == 0.315
        assert shooting_data.fga_by_distance.three_ten == 0.168
        assert shooting_data.fga_by_distance.ten_sixteen == 0.161
        assert shooting_data.fga_by_distance.sixteen_three_pt == 0.211
        assert shooting_data.fga_by_distance.three_point == 0.145

        assert shooting_data.fgp_by_distance.two_point == 0.438
        assert shooting_data.fgp_by_distance.zero_three == 0.604
        assert shooting_data.fgp_by_distance.three_ten == 0.356
        assert shooting_data.fgp_by_distance.ten_sixteen == 0.313
        assert shooting_data.fgp_by_distance.sixteen_three_pt == 0.352
        assert shooting_data.fgp_by_distance.three_point == 0.290

        career_sd = lbj.career_stats.shooting_data
        assert career_sd.dunks_made == 1898
        assert career_sd.dunks_fga == 0.08
        assert career_sd.heaves_made == 2
        assert career_sd.heaves_attempted == 34
        assert career_sd.two_point_fga_assisted == 0.347
        assert career_sd.three_point_fga_assisted == 0.469
        assert career_sd.corner_three_point_fga == 0.129
        assert career_sd.corner_three_point_fgp == 0.387
        assert career_sd.avg_distance == 12.0

        first_playoffs = next(lbj.playoffs)
        assert first_playoffs.shooting_data.avg_distance == 12.1
        assert first_playoffs.shooting_data.dunks_made == 13
