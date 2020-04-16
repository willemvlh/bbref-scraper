from datetime import date

from bballer.models.stats import StatLine
from bballer.scrapers.PlayerPageScraper import PlayerPageScraper
from tests.scrapers.utils import get_resource


class TestPlayerPageScraper:
    carmelo_anthony = PlayerPageScraper(get_resource("carmelo_anthony.html"))
    lebron_james = PlayerPageScraper(get_resource("lebron_james.html"))
    julius_erving = PlayerPageScraper(get_resource("julius_erving.html"))
    ben_wallace = PlayerPageScraper(get_resource("ben_wallace.html"))
    chamberlain = PlayerPageScraper(get_resource("chamberlain.html"))
    shayok = PlayerPageScraper(get_resource("shayok.html"))

    def test_equality(self):
        this_player = self.carmelo_anthony.get_content()
        assert (this_player != self.lebron_james.get_content())
        _set = {this_player, this_player}
        assert len(_set) == 1

    def test__get_name(self):
        assert self.carmelo_anthony._get_name() == "Carmelo Anthony"

    def test_get_dob(self):
        dob = self.carmelo_anthony._get_dob()
        assert isinstance(dob, date)
        assert dob == date(1984, 5, 29)

    def test_get_career_stats(self):
        stats = self.carmelo_anthony._get_career_stats()
        assert isinstance(stats, StatLine)
        assert int(stats.games_started) > 1000

    def test_get_id(self):
        assert self.carmelo_anthony._get_id() == "carmelo_anthony"

    def test_get_shooting_hand(self):
        assert self.carmelo_anthony._get_shooting_hand() == "Right"

    def test_get_college(self):
        assert self.carmelo_anthony._get_college() == "Syracuse"
        assert self.lebron_james._get_college() is None

    def test_player(self):
        player = self.carmelo_anthony.get_content()
        assert len(player.seasons) > 10
        rookie_season = player.seasons[0]
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
        player = self.carmelo_anthony.get_content()
        s = player.seasons[0]
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
        seasons = self.julius_erving._get_regular_season_totals()
        assert len(seasons) == 11  # ABA seasons must be discarded

    def test_game_log(self):
        seasons = PlayerPageScraper(
            "https://www.basketball-reference.com/players/m/mbengdj01.html").get_content().seasons
        gl = seasons[0].game_logs
        assert len([game for game in gl if game.played]) == seasons[0].games_played

    def test_get_physicals(self):
        assert self.carmelo_anthony._get_physicals() == ("6-8", 240)

    def test_get_draft_pick(self):
        assert self.carmelo_anthony._get_draft_pick() == 3
        assert self.ben_wallace._get_draft_pick() is None

    def test_all_star(self):
        assert len([season for season in self.julius_erving._get_regular_season_totals() if season.all_star]) == 11

    def test_get_playoff_totals(self):
        assert len(self.julius_erving._get_playoffs_totals()) == 11
        assert sum([season.points for season in self.julius_erving._get_playoffs_totals()]) == 3088

    def test_historical_player(self):
        player = PlayerPageScraper("https://www.basketball-reference.com/players/h/hawkito01.html").get_content()
        assert player.name == "Tom Hawkins"
        assert player.date_of_birth == date(1936, 12, 22)

    def test_salaries(self):
        anthony = self.carmelo_anthony.get_content()
        assert len(anthony.salaries) == 17
        assert all([sal.amount > 0 for sal in anthony.salaries])
        assert all([sal.team and sal.team.startswith("http") for sal in anthony.salaries])
        assert all([sal.season for sal in anthony.salaries])
        assert sum([sal.amount for sal in anthony.salaries]) > 200000000

    def test_salaries_none(self):
        assert self.chamberlain.get_content().salaries == []

    def test_contract(self):
        james = self.lebron_james.get_content()

        assert james.contract
        assert len(james.contract.years) == 3
        assert all([year.season for year in james.contract.years])
        assert all([year.amount for year in james.contract.years])

        first_year = james.contract.years[0]
        assert first_year.season == "2019-20"
        assert first_year.amount == 37436858
        # assert first_year.option is None

        third_year = james.contract.years[2]
        assert third_year.season == "2021-22"
        assert third_year.amount == 41002273
        # assert third_year.option == "Player"

        chamberlain = self.chamberlain.get_content()
        assert not chamberlain.contract

        shayok = self.shayok.get_content()
        assert not shayok.contract
