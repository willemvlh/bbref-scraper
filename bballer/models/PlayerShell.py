from dataclasses import dataclass

from bballer.models.player import Player
from bballer.scrapers.PlayerPageScraper import PlayerPageScraper


@dataclass
class PlayerShell:
    name: str
    number: int
    url: str

    def __repr__(self):
        return self.name

    def as_player(self) -> Player:
        scr = PlayerPageScraper(self.url)
        return scr.get_content()
