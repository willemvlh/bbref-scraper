from dataclasses import dataclass

from bballer.models.PlayerShell import PlayerShell
from bballer.models.team import TeamShell


@dataclass(frozen=True)
class PlayerInDraft:
    player: PlayerShell
    college: str
    pick: object
    team: TeamShell
    years_in_league: int
