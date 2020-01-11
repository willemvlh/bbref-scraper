from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class TeamSeason:
    season: str
    wins: int
    losses: int
    pace: float
    won_championship: bool
    made_playoffs: bool
    playoff_result: str
    rel_pace: float
    ortg: float
    rel_ortg: float
    drtg: float
    rel_drtg: float
    _team_code: str

    @property
    def roster(self) -> List[Dict]:
        from bballer.scrapers.team import TeamSeasonScraper
        scraper = TeamSeasonScraper(self._team_code, int(self.season[0:4]) + 1)
        return scraper.get_roster()


@dataclass
class Team:
    name: str
    code: str
    seasons: List[TeamSeason]
    wins: int
    losses: int
    championships: int = field(init=False)
    playoff_appearances: int = field(init=False)

    def __post_init__(self):
        self.playoff_appearances = len([s for s in self.seasons if s.made_playoffs])
        self.championships = len([s for s in self.seasons if s.won_championship])

    def season(self, year: str):
        season = [s for s in self.seasons if s.season == year]
        return season[0] if season else None
