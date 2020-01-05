from dataclasses import dataclass
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

    def __post_init__(self):
        self.bpm = self.dbpm + self.obpm
        self.ws = self.ows + self.dws