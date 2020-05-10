from dataclasses import dataclass, field
from typing import Optional, List

from bballer.models.advanced_stats import AdvancedStatLine
from bballer.scrapers.GameLogScraper import GameLogScraper, PlayoffGameLogScraper


@dataclass
class ShootingByDistance:
    two_point: float
    zero_three: float
    three_ten: float
    ten_sixteen: float
    sixteen_three_pt: float
    three_point: float


class ShootingStatLine:
    avg_distance: float
    fga_by_distance: ShootingByDistance
    fgp_by_distance: ShootingByDistance
    dunks_fga: float
    dunks_made: int
    heaves_attempted: int
    heaves_made: int
    two_point_fga_assisted: float
    three_point_fga_assisted: float
    corner_three_point_fga: float
    corner_three_point_fgp: float


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
    shooting_data: ShootingStatLine
    _player_url: str
    _game_logs: List = field(init=False, default=None)
    _round_digits = 3
    game_log_scraper_class = GameLogScraper
    shooting_data_table_id = "shooting"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.season}, {self.team})"

    @property
    def two_fg_percentage(self):
        return self._round(self.two_fg_made / self.two_fg_attempted)

    def _round(self, number: float):
        return round(number, self._round_digits)

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
        if self.three_fg_made and self.three_fg_attempted:
            return self._round(self.three_fg_made / self.three_fg_attempted)

    @property
    def fg_percentage(self):
        if self.fg_made and self.fg_attempted:
            return self._round(self.fg_made / self.fg_attempted)

    @property
    def free_throw_percentage(self):
        if self.ft_made and self.ft_attempted:
            return self._round(self.ft_made / self.ft_attempted)

    @property
    def rebounds(self):
        if self.defensive_rebounds and self.offensive_rebounds:
            return self.defensive_rebounds + self.offensive_rebounds

    def per_game(self):
        pass

    def per_100_possessions(self):
        pass


@dataclass
class PlayoffStatLine(StatLine):
    game_log_scraper_class = PlayoffGameLogScraper
    shooting_data_table_id = "playoffs_shooting"


@dataclass
class CareerStatLine(StatLine):
    def __repr__(self):
        return f"{self.__class__.__name__}(points={self.points}, rebounds={self.rebounds}, assists={self.assists})"
