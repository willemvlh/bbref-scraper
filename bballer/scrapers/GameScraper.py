import logging
from datetime import datetime

from bballer.models.game import Game, CondensedGamelog
from bballer.scrapers.base import Scraper, get_data_stat_in_element


class GameScraper(Scraper):
    def __init__(self, url: str):
        super().__init__(url)

    def get_content(self):
        game = Game()
        teams = self.find_teams()
        game.away_team = teams[0]
        game.home_team = teams[1]
        game.score = self.find_score()
        game.date = self.find_date()
        game.score_by_quarter = self.find_score_by_quarter()
        game.statlines = self.find_statlines()
        return game

    def find_score(self):
        scores = self.find_all("div", class_="score")
        return int(scores[0].get_text()), int(scores[1].get_text())

    def find_teams(self):
        performers = self.find_all("div", itemprop="performer")
        teams = [pf.find("a", itemprop="name").get_text() for pf in performers]
        return teams

    def find_date(self):
        scorebox_div = self.find("div", class_="scorebox_meta")
        if scorebox_div:
            date_div = scorebox_div.find("div")
            date = "" if not date_div else date_div.get_text()
            try:
                return datetime.strptime(date, "%I:%M %p, %B %d, %Y")
            except ValueError:
                logging.debug(f"Could not parse date {date}")
                pass

    def find_score_by_quarter(self):
        scores_table = self.get_commented_table_with_id("line_score")
        score_rows = scores_table.find_all("tr")[-2:]
        score_rows = [
            score_row.find_all(lambda el: el.name == "td" and el.get_text().isnumeric() and not el.find("strong")) for
            score_row in score_rows]
        mapped_rows = [[int(td.get_text()) for td in score_row] for score_row in score_rows]
        return list(zip(mapped_rows[0], mapped_rows[1]))

    def find_statlines(self):
        tables = self.find_all("table", id=lambda x: x.endswith("game-basic"))
        rows = [[tr for tr in table.find_all("tr") if tr.parent.name == "tbody" and tr.find("th", scope="row")] for
                table in tables]
        return [[self.parse_row(row) for row in sublist] for sublist in rows]

    def parse_row(self, row):
        gl = CondensedGamelog()

        gl.player_id = get_data_stat_in_element("player", row, "data-append-csv")
        if get_data_stat_in_element("reason", row):
            gl.played = False
            return gl
        gl.seconds_played = get_data_stat_in_element("mp", row, "csk")
        gl.defensive_rebounds = get_data_stat_in_element("drb", row)
        gl.offensive_rebounds = get_data_stat_in_element("orb", row)
        gl.ft_attempted = get_data_stat_in_element("fta", row)
        gl.ft_made = get_data_stat_in_element("ft", row)
        gl.fg_made = get_data_stat_in_element("fg", row)
        gl.fg_attempted = get_data_stat_in_element("fga", row)
        gl.three_fg_attempted = get_data_stat_in_element("fg3a", row)
        gl.three_fg_made = get_data_stat_in_element("fg3", row)
        gl.assists = get_data_stat_in_element("ast", row)
        gl.steals = get_data_stat_in_element("stl", row)
        gl.turnovers = get_data_stat_in_element("tov", row)
        gl.fouls = get_data_stat_in_element("pf", row)
        gl.points = get_data_stat_in_element("pts", row)
        gl.plus_minus = get_data_stat_in_element("plus_minus", row)
        gl.played = True
        gl.started = len([sibling for sibling in list(row.previous_siblings) if sibling.name == "tr"]) < 5
        return gl
