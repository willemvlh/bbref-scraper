from dataclasses import dataclass
from datetime import date
from typing import List

from bballer.models.stats import StatLine


@dataclass(frozen=True)
class Salary:
    amount: int
    season: str
    team: str


@dataclass(frozen=True)
class Player:
    name: str
    date_of_birth: date
    college: str
    height: str
    weight: int
    position: str
    seasons: List[StatLine]
    playoffs: List[StatLine]
    career_stats: StatLine
    draft_pick: int
    id: str
    shooting_hand: str
    salaries: List[Salary]

    def __repr__(self):
        return f"Player({self.name}, {self.date_of_birth})"

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other.id == self.id
