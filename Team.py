from dataclasses import dataclass
from typing import List

@dataclass
class TeamSeason:
    season: str
    wins: int
    losses: int
    pace: float
    rel_pace: float
    ortg: float
    rel_ortg: float
    drtg: float
    rel_drtg: float


@dataclass
class Team:
    name: str
    code: str
    seasons: List[TeamSeason]
    wins: int
    losses: int
    championships: int
    playoffs: int

