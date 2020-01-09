from dataclasses import dataclass
from typing import List
import json

from Statline import StatLine


@dataclass
class Player:
    name: str
    date_of_birth: str
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

    def __repr__(self):
        return f"Player({self.name}, {self.date_of_birth})"

    def __eq__(self, other):
        return isinstance(other, Player) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.id.__hash__()

    def serialize(self, indent=False) -> str:
        return json.dumps(self, default=lambda obj: obj.__dict__, indent=2 if indent else 0)
