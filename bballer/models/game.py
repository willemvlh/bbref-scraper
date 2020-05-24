from datetime import date
from typing import Tuple, List

from bballer.models.team import TeamShell


class CondensedGamelog(object):
    player_id: str
    seconds_played: int
    played: bool
    started: bool
    seconds_played: int
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
    plus_minus: int
    points: int


class Game:
    home_team: TeamShell
    away_team: TeamShell
    date: date
    score: Tuple[int, int]
    score_by_quarter: List[Tuple[int, int]]
    statlines: List
