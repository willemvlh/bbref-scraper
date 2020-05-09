from datetime import date
from typing import Iterator

from bballer.models.gamelog import GameLog
from bballer.scrapers.base import Scraper
from bballer.scrapers.utilities import *


class GameLogScraper(Scraper):

    def __init__(self, url: str):
        super().__init__(url)

    def get_content(self):
        return self._get_game_logs()

    def get_table(self):
        return self.find("table", id="pgl_basic")

    def _get_game_logs(self) -> Iterator[GameLog]:
        table = self.get_table()
        if not table:
            return
        rows = table.find("tbody").find_all("tr")
        for row in [r for r in rows if "class" not in r.attrs]:
            yield self._parse_row(row)

    def _parse_row(self, row):
        gl = GameLog()
        gl.game_url = to_absolute_url(row.find("td", attrs={"data-stat": "date_game"}).find("a").attrs["href"])
        gl.date = date.fromisoformat(get_data_stat_in_element("date_game", row))
        gl.age = get_data_stat_in_element("age", row)
        gl.team = get_data_stat_in_element("team_id", row)
        gl.opponent = get_data_stat_in_element("opp_id", row)
        gl.result = get_data_stat_in_element("game_result", row)
        gl.started = get_data_stat_in_element("gs", row) == 1
        gl.played = not get_data_stat_in_element("reason", row)
        gl.seconds_played = get_data_stat_in_element("mp", row, "csk") if gl.played else None
        gl.fg_made = get_data_stat_in_element("fg", row) if gl.played else None
        gl.fg_attempted = get_data_stat_in_element("fga", row) if gl.played else None
        gl.three_fg_made = get_data_stat_in_element("fg3", row) if gl.played else None
        gl.three_fg_attempted = get_data_stat_in_element("fg3a", row) if gl.played else None
        gl.ft_made = get_data_stat_in_element("ft", row) if gl.played else None
        gl.ft_attempted = get_data_stat_in_element("fta", row) if gl.played else None
        gl.offensive_rebounds = get_data_stat_in_element("orb", row) if gl.played else None
        gl.defensive_rebounds = get_data_stat_in_element("drb", row) if gl.played else None
        gl.assists = get_data_stat_in_element("ast", row) if gl.played else None
        gl.steals = get_data_stat_in_element("stl", row) if gl.played else None
        gl.blocks = get_data_stat_in_element("blk", row) if gl.played else None
        gl.turnovers = get_data_stat_in_element("tov", row) if gl.played else None
        gl.fouls = get_data_stat_in_element("pf", row) if gl.played else None
        gl.points = get_data_stat_in_element("pts", row) if gl.played else None
        gl.game_score = get_data_stat_in_element("game_score", row) if gl.played else None
        gl.plus_minus = get_data_stat_in_element("plus_minus", row) if gl.played else None

        return gl


class PlayoffGameLogScraper(GameLogScraper):
    def __init__(self, url):
        super().__init__(url)

    def get_table(self):
        return self.get_commented_table_with_id("pgl_basic_playoffs")
