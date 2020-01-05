from dataclasses import dataclass
from typing import Optional
from AdvancedStatLine import AdvancedStatLine


@dataclass
class StatLine:
    season: str
    age: int
    all_star: bool
    minutesPlayed: int
    position: str
    team: str
    gamesPlayed: int
    gamesStarted: int
    fg_made: int
    fg_attempted: int
    two_fg_made: int
    two_fg_attempted: int
    three_fg_made: int
    three_fg_attempted: int
    free_throw_made: int
    free_throw_attempted: int
    offensive_rebounds: int
    defensive_rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fouls: int
    points: int
    effective_fg_percentage: int
    #advanced: Optional[AdvancedStatLine]

    @property
    def two_fg_percentage(self):
        return self.two_fg_made / self.two_fg_attempted

    @property
    def three_fg_percentage(self):
        return self.three_fg_made / self.three_fg_attempted

    @property
    def fg_percentage(self):
        return self.fg_made / self.fg_attempted

    @property
    def free_throw_percentage(self):
        return self.free_throw_made / self.free_throw_attempted

    @property
    def rebounds(self):
        return self.defensive_rebounds + self.offensive_rebounds