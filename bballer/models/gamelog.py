from datetime import date
from functools import lru_cache

from bballer.scrapers.GameScraper import GameScraper


class GameLog:
    date: date
    team: str
    age: str
    opponent: str
    played: bool
    started: bool
    seconds_played: int
    result: str
    fg_made: int
    fg_attempted: int
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
    game_score: float
    plus_minus: int
    points: int
    game_url: str

    def __repr__(self):
        return f"GameLog(points={self.points}, rebounds={self.rebounds}, assists={self.assists})"

    @property
    def rebounds(self):
        if None in [self.offensive_rebounds, self.defensive_rebounds]:
            return None
        return self.offensive_rebounds + self.defensive_rebounds

    @lru_cache(None)
    def to_game(self):
        assert self.game_url is not None
        scr = GameScraper(self.game_url)
        return scr.get_content()
