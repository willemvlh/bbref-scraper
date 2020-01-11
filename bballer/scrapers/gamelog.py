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
        gl.seconds_played = self._get_data_stat_in_element("mp", row, "csk") if gl.played else None
        gl.fg = self._get_data_stat_in_element("fg", row) if gl.played else None
        gl.fga = self._get_data_stat_in_element("fga", row) if gl.played else None
        gl.tp = self._get_data_stat_in_element("fg3", row) if gl.played else None
        gl.tpa = self._get_data_stat_in_element("fg3a", row) if gl.played else None
        gl.ft = self._get_data_stat_in_element("ft", row) if gl.played else None
        gl.fta = self._get_data_stat_in_element("fta", row) if gl.played else None
        gl.orb = self._get_data_stat_in_element("orb", row) if gl.played else None
        gl.drb = self._get_data_stat_in_element("drb", row) if gl.played else None
        gl.ast = self._get_data_stat_in_element("ast", row) if gl.played else None
        gl.stl = self._get_data_stat_in_element("stl", row) if gl.played else None
        gl.blk = self._get_data_stat_in_element("blk", row) if gl.played else None
        gl.tov = self._get_data_stat_in_element("tov", row) if gl.played else None
        gl.pf = self._get_data_stat_in_element("pf", row) if gl.played else None
        gl.points = self._get_data_stat_in_element("pts", row) if gl.played else None
        gl.game_score = self._get_data_stat_in_element("game_score", row) if gl.played else None
        gl.plus_minus = self._get_data_stat_in_element("plus_minus", row) if gl.played else None

        return gl
