from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from bballer.models.stats import StatLine
from bballer.models.team import TeamShell


@dataclass(frozen=True)
class DraftPick:
    round: Optional[int]
    pick: Optional[int]
    overall: Optional[int]
    year: int
    team: TeamShell


@dataclass(frozen=True)
class Salary:
    amount: int
    season: str
    team: str


@dataclass(frozen=True)
class ContractYear:
    season: str
    amount: int
    option: Optional[str]


@dataclass(frozen=True)
class Contract:
    years: List[ContractYear]


@dataclass(frozen=True)
class Player:
    name: str
    date_of_birth: date
    college: str
    _height: int
    _weight: int
    position: str
    seasons: List[StatLine]  # todo: should be generator
    playoffs: List[StatLine]  # todo: should be generator
    career_stats: StatLine
    draft_pick: DraftPick
    id: str
    shooting_hand: str
    contract: Contract
    salaries: List[Salary]

    def __repr__(self):
        return f"Player({self.name}, {self.date_of_birth})"

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other.id == self.id

    @property
    def height_in(self) -> int:
        return self._height

    @property
    def height_cm(self) -> int:
        return self._height and round(self._height * 2.54)

    @property
    def weight_kg(self):
        return self._weight and round(self._weight / 2.205)

    @property
    def weight_lb(self):
        return self._weight
