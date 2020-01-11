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
    fg: int
    fga: int
    tp: int
    tpa: int
    ft: int
    fta: int
    orb: int
    drb: int
    ast: int
    stl: int
    blk: int
    tov: int
    pf: int
    game_score: float
    plus_minus: int
    points: int