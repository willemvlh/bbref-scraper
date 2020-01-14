import logging
import os
import re

from bs4 import Comment, BeautifulSoup

from bballer.models.player import Player
from bballer.models.stats import StatLine, AdvancedStatLine
from bballer.scrapers.base import Scraper


class PlayerPageScraper(Scraper):
    def __init__(self, url: str):
        super().__init__(url)
        self._reg_season_table = self._get_table_with_id("totals")
        self._playoff_table = self._get_table_with_id("playoffs_totals")
        self._advanced_table = self._get_table_with_id("advanced")

    def player(self) -> Player:
        id_ = self._get_id()
        name = self._get_name()
        seasons = self._get_regular_season_totals()
        playoffs = self._get_playoffs_totals()
        college = self._get_college()
        date_of_birth = self._get_dob()
        career_stats = self._get_career_stats()
        height, weight = self._get_physicals()
        draft_pick = self._get_draft_pick()
        positions = [season.position for season in seasons]
        position = max(positions, key=positions.count) if positions else None
        shooting_hand = self._get_shooting_hand()
        logging.debug(f"Processed {name}")
        return Player(id=id_, name=name, seasons=seasons, playoffs=playoffs, college=college,
                      date_of_birth=date_of_birth,
                      career_stats=career_stats, height=height, weight=weight, draft_pick=draft_pick, position=position,
                      shooting_hand=shooting_hand)

    def _get_id(self):
        if os.path.isfile(self._url):
            return os.path.split(self._url)[-1].rstrip(".html")
        id_ = self._url.split("/")[-1].rstrip(".html")
        if not id_:
            raise ValueError("Player has no id!")
        return id_

    def _get_physicals(self):
        return self._safe_get_item_prop("height"), int(self._safe_get_item_prop("weight").rstrip("lb"))

    def _get_name(self) -> str:
        return self._safe_get_item_prop("name", element="h1")

    def _get_table_with_id(self, _id):
        # tables are embedded as comments in the document, so we have to fish
        comment = self._parsed.find(string=lambda x: isinstance(x, Comment) and f"id=\"{_id}\"" in x)
        if not comment:
            return
        parsed = BeautifulSoup(comment, features="html.parser")
        return parsed.find("table", id=_id)

    def _get_career_stats(self):
        if self._reg_season_table:
            career_row = self._reg_season_table.find("th", string="Career").find_parent("tr")
            return self._parse_stats_from_row(career_row)

    def _get_college(self):
        preceding_element = self._parsed.find("strong", text=re.compile("College:"))
        if preceding_element:
            return preceding_element.find_next_sibling("a").text

    def _get_regular_season_totals(self):
        return self._get_totals(self._reg_season_table)

    def _get_playoffs_totals(self):
        return self._get_totals(self._playoff_table)

    def _get_totals(self, table):
        if not table:
            return []
        rows = table.find_all("tr", class_="full_table")
        totals = []
        for row in rows:
            if self._get_data_stat_in_element("lg_id", row) == "NBA":
                season = self._parse_stats_from_row(row)
                totals.append(season)
        return totals

    def _parse_stats_from_row(self, row):
        season = self._get_season_from_row(row)
        age = self._get_data_stat_in_element("age", row)
        team = self._get_data_stat_in_element("team_id", row)
        all_star = bool(row.find("span", class_="sr_star"))
        games_played = self._get_data_stat_in_element("g", row)
        games_started = self._get_data_stat_in_element("gs", row)
        minutes_played = self._get_data_stat_in_element("mp", row)
        position = self._get_data_stat_in_element("pos", row)
        fg_made = self._get_data_stat_in_element("fg", row)
        fg_attempted = self._get_data_stat_in_element("fga", row)
        three_fg_made = self._get_data_stat_in_element("fg3", row)
        three_fg_attempted = self._get_data_stat_in_element("fg3a", row)
        two_fg_made = self._get_data_stat_in_element("fg2", row)
        two_fg_attempted = self._get_data_stat_in_element("fg2a", row)
        effective_fg_percentage = self._get_data_stat_in_element("efg_pct", row)
        free_throw_made = self._get_data_stat_in_element("ft", row)
        free_throw_attempted = self._get_data_stat_in_element("fta", row)
        offensive_rebounds = self._get_data_stat_in_element("orb", row)
        defensive_rebounds = self._get_data_stat_in_element("drb", row)
        assists = self._get_data_stat_in_element("ast", row)
        steals = self._get_data_stat_in_element("stl", row)
        blocks = self._get_data_stat_in_element("blk", row)
        turnovers = self._get_data_stat_in_element("tov", row)
        fouls = self._get_data_stat_in_element("pf", row)
        points = self._get_data_stat_in_element("pts", row)
        statline = StatLine(season=season, age=age, all_star=all_star, games_played=games_played,
                            games_started=games_started,
                            minutes_played=minutes_played, team=team,
                            position=position, fg_made=fg_made, fg_attempted=fg_attempted, three_fg_made=three_fg_made,
                            three_fg_attempted=three_fg_attempted, two_fg_made=two_fg_made,
                            two_fg_attempted=two_fg_attempted, effective_fg_percentage=effective_fg_percentage,
                            ft_made=free_throw_made, ft_attempted=free_throw_attempted,
                            offensive_rebounds=offensive_rebounds, defensive_rebounds=defensive_rebounds,
                            assists=assists, steals=steals, blocks=blocks, turnovers=turnovers, fouls=fouls,
                            points=points, _player_url=self._url)
        advanced_statline_rows = [tr for tr in self._advanced_table.find_all("tr", class_="full_table") if
                                  self._get_season_from_row(tr) == season]
        if advanced_statline_rows:
            advanced_statline = self._parse_stats_from_advanced_row(advanced_statline_rows[0], statline)
            statline.advanced = advanced_statline
        return statline

    def _parse_stats_from_advanced_row(self, row, season):
        per = self._get_data_stat_in_element("per", row)
        tsp = self._get_data_stat_in_element("ts_pct", row)
        orb = self._get_data_stat_in_element("orb_pct", row)
        tpar = self._get_data_stat_in_element("fg3a_per_fga_pct", row)
        ftar = self._get_data_stat_in_element("fta_per_fga_pct", row)
        drb = self._get_data_stat_in_element("drb_pct", row)
        trb = self._get_data_stat_in_element("trb_pct", row)
        astp = self._get_data_stat_in_element("ast_pct", row)
        stlp = self._get_data_stat_in_element("stl_pct", row)
        blkp = self._get_data_stat_in_element("blk_pct", row)
        tovp = self._get_data_stat_in_element("tov_pct", row)
        usgp = self._get_data_stat_in_element("usg_pct", row)
        ows = self._get_data_stat_in_element("ows", row)
        dws = self._get_data_stat_in_element("dws", row)
        wsp48 = self._get_data_stat_in_element("ws_per_48", row)
        obpm = self._get_data_stat_in_element("obpm", row)
        dbpm = self._get_data_stat_in_element("dbpm", row)
        vorp = self._get_data_stat_in_element("vorp", row)

        return AdvancedStatLine(season=season, player_efficiency_rating=per, true_shooting_percentage=tsp,
                                offensive_rebound_percentage=orb, defensive_rebound_percentage=drb,
                                total_rebound_percentage=trb, assist_percentage=astp, steal_percentage=stlp,
                                three_fg_attempt_rate=tpar, ft_attempt_rate=ftar,
                                block_percentage=blkp, turnover_percentage=tovp, usage_percentage=usgp, offensive_win_shares=ows, defensive_win_shares=dws,
                                win_shares_per_48=wsp48, offensive_box_plus_minus=obpm, defensive_box_plus_minus=dbpm, value_over_replacement_player=vorp)

    def _get_dob(self):
        return self._safe_get_item_prop("birthDate", attr="data-birth")

    def _get_draft_pick(self):
        element = self._parsed.find("strong", string=re.compile("Draft:"))
        if element:
            s = element.find_next_sibling(string=re.compile("overall"))
            if s:
                matches = re.findall(r"\d{1,2}[a-z]{1,3} overall", s.string)
                if matches:
                    return int("".join([c for c in matches[0] if c.isdigit()]))

    def _get_shooting_hand(self) -> str:
        return self._get_text_sibling("strong", "Shoots:")

    def _get_season_from_row(self, row):
        s = self._get_data_stat_in_element("season", row)
        return 0 if "Career" in s else int(s[0:4]) + 1


class PlayerListScraper(Scraper):
    def __init__(self, url: str):
        super().__init__(url)

    def get_player_urls(self):
        cells = self._parsed.find_all("th", {"data-stat": "player", "scope": "row"})
        return ["https://www.basketball-reference.com" + cell.find_next("a").attrs["href"] for cell in cells]
