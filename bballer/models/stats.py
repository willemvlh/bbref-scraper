from dataclasses import dataclass, field
from typing import Optional, Any, List

from bballer.scrapers.GameLogScraper import GameLogScraper, PlayoffGameLogScraper


@dataclass
class AdvancedStatLine:
    season: Any
    player_efficiency_rating: float
    true_shooting_percentage: float
    three_fg_attempt_rate: float
    ft_attempt_rate: float
    offensive_rebound_percentage: float
    defensive_rebound_percentage: float
    total_rebound_percentage: float
    assist_percentage: float
    steal_percentage: float
    block_percentage: float
    turnover_percentage: float
    usage_percentage: float
    offensive_win_shares: float
    defensive_win_shares: float
    win_shares_per_48: float
    offensive_box_plus_minus: float
    defensive_box_plus_minus: float
    value_over_replacement_player: float
    box_plus_minus: float = field(init=False)
    win_shares: float = field(init=False)

    def __repr__(self):
        return f"Statline({self.season})"

    def __post_init__(self):
        if self.defensive_box_plus_minus and self.offensive_box_plus_minus:
            self.box_plus_minus = self.defensive_box_plus_minus + self.offensive_box_plus_minus
        if self.offensive_win_shares and self.defensive_win_shares:
            self.win_shares = self.offensive_win_shares + self.defensive_win_shares


def per_game():
    pass


@dataclass
class StatLine:
    season: int
    age: int
    all_star: bool
    minutes_played: int
    position: str
    team: str
    games_played: int
    games_started: int
    fg_made: int
    fg_attempted: int
    two_fg_made: int
    two_fg_attempted: int
    three_fg_made: int
    three_fg_attempted: int
    ft_made: int
    ft_attempted: int
    offensive_rebounds: int
    defensive_rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fouls: int
    points: int
    effective_fg_percentage: float
    advanced: Optional[AdvancedStatLine] = field(init=False, repr=False)
    _player_url: str
    _game_logs: List = field(init=False, default=None)
    game_log_scraper_class = GameLogScraper

    def __repr__(self):
        return f"{self.__class__.__name__}({self.season}, {self.team})"

    @property
    def two_fg_percentage(self):
        return self.two_fg_made / self.two_fg_attempted

    def game_logs(self):
        if not self._game_logs:
            scr = self.game_log_scraper_class(
                self._get_game_log_url())
            self._game_logs = scr.get_content()
        return self._game_logs

    def _get_game_log_url(self):
        return self._player_url.rstrip(".html") + f"/gamelog/{self.season}"

    @property
    def three_fg_percentage(self):
        return self.three_fg_made / self.three_fg_attempted

    @property
    def fg_percentage(self):
        return self.fg_made / self.fg_attempted

    @property
    def free_throw_percentage(self):
        return self.ft_made / self.ft_attempted

    @property
    def rebounds(self):
        return self.defensive_rebounds + self.offensive_rebounds

    def per_game(self):
        pass

    def per_100_possessions(self):
        pass


@dataclass
class PlayoffStatLine(StatLine):
    game_log_scraper_class = PlayoffGameLogScraper


@dataclass
class CareerStatLine(StatLine):
    def __repr__(self):
        return f"{self.__class__.__name__}(points={self.points}, rebounds={self.rebounds}, assists={self.assists})"
