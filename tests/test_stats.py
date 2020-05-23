from bballer.scrapers.PlayerPageScraper import PlayerPageScraper
from tests.scrapers.utils import get_resource


class TestStats:
    player = PlayerPageScraper(get_resource("carmelo_anthony.html")).get_content()
    seasons = list(player.seasons)
    rookie_season = seasons[0]

    def test_season_stats(self):
        rookie_season = self.rookie_season
        assert repr(rookie_season).endswith("(2004, DEN)")
        assert rookie_season.stats.position == "SF"
        assert rookie_season.season == 2004
        assert rookie_season.stats.games_started == 82
        assert rookie_season.stats.games_played == 82
        assert rookie_season.stats.minutes_played == 2995
        assert rookie_season.stats.fg_attempted == 1465
        assert rookie_season.stats.fg_made == 624
        assert rookie_season.stats.three_fg_made == 69
        assert rookie_season.stats.three_fg_attempted == 214
        assert rookie_season.stats.two_fg_attempted == 1251
        assert rookie_season.stats.two_fg_made == 555
        assert rookie_season.stats.effective_fg_percentage == 0.449
        assert rookie_season.stats.ft_made == 408
        assert rookie_season.stats.ft_attempted == 525
        assert rookie_season.stats.offensive_rebounds == 183
        assert rookie_season.stats.defensive_rebounds == 315
        assert rookie_season.stats.rebounds == 498
        assert round(rookie_season.stats.two_fg_percentage, 3) == 0.444
        assert rookie_season.stats.fg_percentage == 0.426
        assert rookie_season.stats.three_fg_percentage == 0.322
        assert rookie_season.stats.free_throw_percentage == 0.777
        assert not rookie_season.all_star
        assert rookie_season.stats.assists == 227
        assert rookie_season.stats.blocks == 41
        assert rookie_season.stats.turnovers == 247
        assert rookie_season.stats.steals == 97
        assert rookie_season.stats.fouls == 225
        assert rookie_season.stats.points == 1725

    def test_advanced_stats(self):
        rookie_season = self.rookie_season
        assert repr(rookie_season.stats.advanced) == "AdvancedStatLine(2004)"
        assert rookie_season.stats.advanced.assist_percentage == 13.8
        assert rookie_season.stats.advanced.player_efficiency_rating == 17.6
        assert rookie_season.stats.advanced.true_shooting_percentage == 0.509
        assert rookie_season.stats.advanced.three_fg_attempt_rate == 0.146
        assert rookie_season.stats.advanced.ft_attempt_rate == 0.358
        assert rookie_season.stats.advanced.offensive_rebound_percentage == 6.8
        assert rookie_season.stats.advanced.defensive_rebound_percentage == 12.1
        assert rookie_season.stats.advanced.total_rebound_percentage == 9.4
        assert rookie_season.stats.advanced.steal_percentage == 1.7
        assert rookie_season.stats.advanced.block_percentage == 1.0
        assert rookie_season.stats.advanced.turnover_percentage == 12.7
        assert rookie_season.stats.advanced.usage_percentage == 28.5
        assert rookie_season.stats.advanced.offensive_win_shares == 3.7
        assert rookie_season.stats.advanced.defensive_win_shares == 2.4
        assert rookie_season.stats.advanced.win_shares == 6.1
        assert rookie_season.stats.advanced.win_shares_per_48 == 0.098
        assert rookie_season.stats.advanced.offensive_box_plus_minus == 1.2
        assert rookie_season.stats.advanced.defensive_box_plus_minus == -1.2
        assert rookie_season.stats.advanced.box_plus_minus == 0
        assert rookie_season.stats.advanced.value_over_replacement_player == 1.6

    def test_stats_where_none_available(self):
        chamberlain = PlayerPageScraper(get_resource("chamberlain.html")).get_content()
        rookie_season = next(chamberlain.seasons)
        assert rookie_season.stats.rebounds is None
        assert rookie_season.stats.offensive_rebounds is None
        assert rookie_season.stats.defensive_rebounds is None
        assert rookie_season.stats.turnovers is None
        assert rookie_season.stats.three_fg_percentage is None
        assert rookie_season.stats.three_fg_made is None
        assert rookie_season.stats.three_fg_attempted is None
        assert rookie_season.stats.shooting_data is None

        advanced_stats = rookie_season.stats.advanced
        assert advanced_stats.value_over_replacement_player is None
        assert advanced_stats.ft_attempt_rate == 0.429
        assert advanced_stats.assist_percentage is None
        assert advanced_stats.offensive_rebound_percentage is None
        assert advanced_stats.defensive_rebound_percentage is None
        assert advanced_stats.usage_percentage is None

    def test_stats_where_partially_available(self):
        mullin = PlayerPageScraper(get_resource("chris_mullin.html")).get_content()
        seasons = list(mullin.seasons)
        rookie_season = seasons[0]
        assert rookie_season.stats.shooting_data is None
        final_season = seasons[-1]
        assert final_season.stats.shooting_data
        assert final_season.stats.shooting_data.avg_distance == 18.8

    def test_career_stats_advanced(self):
        mullin = PlayerPageScraper(get_resource("chris_mullin.html")).get_content()
        assert mullin.career_stats.advanced.usage_percentage

    def test_career_stats_encapsulated(self):
        mullin = PlayerPageScraper(get_resource("chris_mullin.html")).get_content()
        career_stats = mullin.career_stats
        first_season = next(mullin.seasons)
        first_playoffs = next(mullin.playoffs)

        for attr in ["age", "all_star", "team", "season"]:
            assert not hasattr(career_stats, attr)
            assert hasattr(first_season, attr)
            assert hasattr(first_playoffs, attr)
