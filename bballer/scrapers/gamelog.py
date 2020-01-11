from typing import List, Optional

from bballer.models.gamelog import GameLog
from bballer.scrapers.base import Scraper


class GameLogScraper(Scraper):
    def get_game_logs(self) -> Optional[List[GameLog]]:
        table = self._find("table", id="pgl_basic")
        if not table:
            return
        rows = table.find("tbody").find_all("tr")
        return [self._parse_row(row) for row in rows if "class" not in row.attrs]

    def _parse_row(self, row):
        gl = GameLog()
        gl.date = self._get_data_stat_in_element("date_game", row)
        gl.age = self._get_data_stat_in_element("age", row)
        gl.team = self._get_data_stat_in_element("team_id", row)
        gl.opponent = self._get_data_stat_in_element("opp_id", row)
        gl.result = self._get_data_stat_in_element("game_result", row)
        gl.started = self._get_data_stat_in_element("gs", row) == 1
        gl.played = not self._get_data_stat_in_element("reason", row)
        if gl.played:
            gl.seconds_played = self._get_data_stat_in_element("mp", row, "csk")
            gl.fg = self._get_data_stat_in_element("fg", row)
            gl.fga = self._get_data_stat_in_element("fga", row)
            gl.tp = self._get_data_stat_in_element("fg3", row)
            gl.tpa = self._get_data_stat_in_element("fg3a", row)
            gl.ft = self._get_data_stat_in_element("ft", row)
            gl.fta = self._get_data_stat_in_element("fta", row)
            gl.orb = self._get_data_stat_in_element("orb", row)
            gl.drb = self._get_data_stat_in_element("drb", row)
            gl.ast = self._get_data_stat_in_element("ast", row)
            gl.stl = self._get_data_stat_in_element("stl", row)
            gl.blk = self._get_data_stat_in_element("blk", row)
            gl.tov = self._get_data_stat_in_element("tov", row)
            gl.pf = self._get_data_stat_in_element("pf", row)
            gl.points = self._get_data_stat_in_element("pts", row)
            gl.game_score = self._get_data_stat_in_element("game_score", row)
            gl.plus_minus = self._get_data_stat_in_element("plus_minus", row)

        return gl