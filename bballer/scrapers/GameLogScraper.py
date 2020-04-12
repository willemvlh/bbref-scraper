from datetime import date
from typing import List, Optional

from bballer.models.gamelog import GameLog
from bballer.scrapers.base import Scraper
from bballer.scrapers.utilities import *


class GameLogScraper(Scraper):

    def get_content(self):
        return self._get_game_logs()

    def _get_game_logs(self) -> Optional[List[GameLog]]:
        table = self.find("table", id="pgl_basic")
        if not table:
            return
        rows = table.find("tbody").find_all("tr")
        return [self._parse_row(row) for row in rows if "class" not in row.attrs]

    def _parse_row(self, row):
        gl = GameLog()
        gl.game_url = to_absolute_url(row.find("td", attrs={"data-stat": "date_game"}).find("a").attrs["href"])
        gl.date = date.fromisoformat(self.get_data_stat_in_element("date_game", row))
        gl.age = self.get_data_stat_in_element("age", row)
        gl.team = self.get_data_stat_in_element("team_id", row)
        gl.opponent = self.get_data_stat_in_element("opp_id", row)
        gl.result = self.get_data_stat_in_element("game_result", row)
        gl.started = self.get_data_stat_in_element("gs", row) == 1
        gl.played = not self.get_data_stat_in_element("reason", row)
        gl.seconds_played = self.get_data_stat_in_element("mp", row, "csk") if gl.played else None
        gl.fg_made = self.get_data_stat_in_element("fg", row) if gl.played else None
        gl.fg_attempted = self.get_data_stat_in_element("fga", row) if gl.played else None
        gl.three_fg_made = self.get_data_stat_in_element("fg3", row) if gl.played else None
        gl.three_fg_attempted = self.get_data_stat_in_element("fg3a", row) if gl.played else None
        gl.ft_made = self.get_data_stat_in_element("ft", row) if gl.played else None
        gl.ft_attempted = self.get_data_stat_in_element("fta", row) if gl.played else None
        gl.offensive_rebounds = self.get_data_stat_in_element("orb", row) if gl.played else None
        gl.defensive_rebounds = self.get_data_stat_in_element("drb", row) if gl.played else None
        gl.assists = self.get_data_stat_in_element("ast", row) if gl.played else None
        gl.steals = self.get_data_stat_in_element("stl", row) if gl.played else None
        gl.blocks = self.get_data_stat_in_element("blk", row) if gl.played else None
        gl.turnovers = self.get_data_stat_in_element("tov", row) if gl.played else None
        gl.fouls = self.get_data_stat_in_element("pf", row) if gl.played else None
        gl.points = self.get_data_stat_in_element("pts", row) if gl.played else None
        gl.game_score = self.get_data_stat_in_element("game_score", row) if gl.played else None
        gl.plus_minus = self.get_data_stat_in_element("plus_minus", row) if gl.played else None

        return gl
