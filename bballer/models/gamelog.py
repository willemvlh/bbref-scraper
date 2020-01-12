from dataclasses import dataclass
from datetime import date

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