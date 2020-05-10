from bballer.scrapers.PlayerPageScraper import PlayerPageScraper
from tests.scrapers.utils import get_resource


class TestStats:
    player = PlayerPageScraper(get_resource("carmelo_anthony.html")).get_content()
    seasons = list(player.seasons)
    rookie_season = seasons[0]

    def test_season_stats(self):
        rookie_season = self.rookie_season
        assert repr(rookie_season) == "StatLine(2004, DEN)"
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
        assert round(rookie_season.two_fg_percentage, 3) == 0.444
        assert rookie_season.fg_percentage == 0.426
        assert rookie_season.three_fg_percentage == 0.322
        assert rookie_season.free_throw_percentage == 0.777
        assert not rookie_season.all_star
        assert rookie_season.assists == 227
        assert rookie_season.blocks == 41
        assert rookie_season.turnovers == 247
        assert rookie_season.steals == 97
        assert rookie_season.fouls == 225
        assert rookie_season.points == 1725

    def test_advanced_stats(self):
        rookie_season = self.rookie_season
        assert repr(rookie_season.advanced) == "AdvancedStatLine(2004)"
        assert rookie_season.advanced.assist_percentage == 13.8
        assert rookie_season.advanced.player_efficiency_rating == 17.6
        assert rookie_season.advanced.true_shooting_percentage == 0.509
        assert rookie_season.advanced.three_fg_attempt_rate == 0.146
        assert rookie_season.advanced.ft_attempt_rate == 0.358
        assert rookie_season.advanced.offensive_rebound_percentage == 6.8
        assert rookie_season.advanced.defensive_rebound_percentage == 12.1
        assert rookie_season.advanced.total_rebound_percentage == 9.4
        assert rookie_season.advanced.steal_percentage == 1.7
        assert rookie_season.advanced.block_percentage == 1.0
        assert rookie_season.advanced.turnover_percentage == 12.7
        assert rookie_season.advanced.usage_percentage == 28.5
        assert rookie_season.advanced.offensive_win_shares == 3.7
        assert rookie_season.advanced.defensive_win_shares == 2.4
        assert rookie_season.advanced.win_shares == 6.1
        assert rookie_season.advanced.win_shares_per_48 == 0.098
        assert rookie_season.advanced.offensive_box_plus_minus == 1.2
        assert rookie_season.advanced.defensive_box_plus_minus == -1.2
        assert rookie_season.advanced.box_plus_minus == 0
        assert rookie_season.advanced.value_over_replacement_player == 1.6

    def test_stats_where_none_available(self):
        chamberlain = PlayerPageScraper(get_resource("chamberlain.html")).get_content()
        rookie_season = next(chamberlain.seasons)
        assert rookie_season.rebounds is None
        assert rookie_season.offensive_rebounds is None
        assert rookie_season.defensive_rebounds is None
        assert rookie_season.turnovers is None
        assert rookie_season.three_fg_percentage is None
        assert rookie_season.three_fg_made is None
        assert rookie_season.three_fg_attempted is None
        assert rookie_season.shooting_data is None

        advanced_stats = rookie_season.advanced
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
        assert rookie_season.shooting_data is None
        final_season = seasons[-1]
        assert final_season.shooting_data
        assert final_season.shooting_data.avg_distance == 18.8
