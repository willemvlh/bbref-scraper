from dataclasses import dataclass, field
from typing import Any


@dataclass
class AdvancedStatLine:
    season: Any
    per: float
    tsp: float
    tpar: float
    ftar: float
    orb: float
    drb: float
    trb: float
    astp: float
    stlp: float
    blkp: float
    tovp: float
    usgp: float
    ows: float
    dws: float
    wsp48: float
    obpm: float
    dbpm: float
    vorp: float
    bpm: float = field(init=False)
    ws: float = field(init=False)

    def __repr__(self):
        return f"Statline({self.season})"

    def __post_init__(self):
        if self.dbpm and self.obpm:
            self.bpm = self.dbpm + self.obpm
        if self.ows and self.dws:
            self.ws = self.ows + self.dws
