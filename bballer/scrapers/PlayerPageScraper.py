import logging
import os
import re
from datetime import date
from typing import List, Optional

from bballer.models.player import Player, Salary, Contract, ContractYear
from bballer.models.stats import StatLine, AdvancedStatLine
from bballer.scrapers.base import Scraper
from bballer.scrapers.utilities import to_absolute_url


def _get_contract_option(classes: List) -> Optional[str]:
    if not classes:
        return None
    option_map = {"salary-pl": "player", "salary-tm": "team", "salary-et": "early termination"}
    for cl in classes:
        try:
            return option_map[cl]
        except KeyError:
            continue
    return None


class PlayerPageScraper(Scraper):
    def get_content(self):
        return self.player()

    def __init__(self, url: str):
        super().__init__(url)
        self._reg_season_table = self.get_commented_table_with_id("totals")
        self._playoff_table = self.get_commented_table_with_id("playoffs_totals")
        self._advanced_table = self.get_commented_table_with_id("advanced")

    def player(self) -> Player:
        id_ = self._get_id()
        name = self._get_name()
        seasons = self._get_regular_season_totals()
        playoffs = self._get_playoffs_totals()
        college = self._get_college()
        date_of_birth = self._get_dob()
        career_stats = self._get_career_stats()
        height, weight = self._get_physical()
        draft_pick = self._get_draft_pick()
        positions = [season.position for season in seasons]
        position = max(positions, key=positions.count) if positions else None
        shooting_hand = self._get_shooting_hand()
        salaries = self._get_salaries()
        contract = self._get_contract()
        logging.debug(f"Processed {name}")
        return Player(id=id_, name=name, seasons=seasons, playoffs=playoffs, college=college,
                      date_of_birth=date_of_birth,
                      career_stats=career_stats, _height=height, _weight=weight, draft_pick=draft_pick,
                      position=position, shooting_hand=shooting_hand, salaries=salaries, contract=contract)

    def _get_id(self):
        if os.path.isfile(self._url):
            return os.path.split(self._url)[-1].rstrip(".html")
        id_ = self._url.split("/")[-1].rstrip(".html")
        if not id_:
            raise ValueError("Player has no id!")
        return id_

    def _get_physical(self):
        height = self.get_item_prop("height")
        if height:
            feet, inch = tuple([int(x) for x in height.split("-")])
            height = feet * 12 + inch
        weight = int(self.get_item_prop("weight").rstrip("lb"))
        return height, weight

    def _get_name(self) -> str:
        return self.get_item_prop("name", element="h1")

    def _get_career_stats(self):
        if self._reg_season_table:
            career_row = self._reg_season_table.find("th", string="Career").find_parent("tr")
            return self._parse_stats_from_row(career_row)

    def _get_college(self):
        preceding_element = self._parsed.find("strong", text=re.compile("College:"))
        if preceding_element and preceding_element.find_next_sibling("a"):
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
            if self.get_data_stat_in_element("lg_id", row) == "NBA":
                season = self._parse_stats_from_row(row)
                totals.append(season)
        return totals

    def _parse_stats_from_row(self, row):
        season = self._get_season_from_row(row)
        age = self.get_data_stat_in_element("age", row)
        team = self.get_data_stat_in_element("team_id", row)
        all_star = bool(row.find("span", class_="sr_star"))
        games_played = self.get_data_stat_in_element("g", row)
        games_started = self.get_data_stat_in_element("gs", row)
        minutes_played = self.get_data_stat_in_element("mp", row)
        position = self.get_data_stat_in_element("pos", row)
        fg_made = self.get_data_stat_in_element("fg", row)
        fg_attempted = self.get_data_stat_in_element("fga", row)
        three_fg_made = self.get_data_stat_in_element("fg3", row)
        three_fg_attempted = self.get_data_stat_in_element("fg3a", row)
        two_fg_made = self.get_data_stat_in_element("fg2", row)
        two_fg_attempted = self.get_data_stat_in_element("fg2a", row)
        effective_fg_percentage = self.get_data_stat_in_element("efg_pct", row)
        free_throw_made = self.get_data_stat_in_element("ft", row)
        free_throw_attempted = self.get_data_stat_in_element("fta", row)
        offensive_rebounds = self.get_data_stat_in_element("orb", row)
        defensive_rebounds = self.get_data_stat_in_element("drb", row)
        assists = self.get_data_stat_in_element("ast", row)
        steals = self.get_data_stat_in_element("stl", row)
        blocks = self.get_data_stat_in_element("blk", row)
        turnovers = self.get_data_stat_in_element("tov", row)
        fouls = self.get_data_stat_in_element("pf", row)
        points = self.get_data_stat_in_element("pts", row)
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
        per = self.get_data_stat_in_element("per", row)
        tsp = self.get_data_stat_in_element("ts_pct", row)
        orb = self.get_data_stat_in_element("orb_pct", row)
        tpar = self.get_data_stat_in_element("fg3a_per_fga_pct", row)
        ftar = self.get_data_stat_in_element("fta_per_fga_pct", row)
        drb = self.get_data_stat_in_element("drb_pct", row)
        trb = self.get_data_stat_in_element("trb_pct", row)
        astp = self.get_data_stat_in_element("ast_pct", row)
        stlp = self.get_data_stat_in_element("stl_pct", row)
        blkp = self.get_data_stat_in_element("blk_pct", row)
        tovp = self.get_data_stat_in_element("tov_pct", row)
        usgp = self.get_data_stat_in_element("usg_pct", row)
        ows = self.get_data_stat_in_element("ows", row)
        dws = self.get_data_stat_in_element("dws", row)
        wsp48 = self.get_data_stat_in_element("ws_per_48", row)
        obpm = self.get_data_stat_in_element("obpm", row)
        dbpm = self.get_data_stat_in_element("dbpm", row)
        vorp = self.get_data_stat_in_element("vorp", row)

        return AdvancedStatLine(season=season, player_efficiency_rating=per, true_shooting_percentage=tsp,
                                offensive_rebound_percentage=orb, defensive_rebound_percentage=drb,
                                total_rebound_percentage=trb, assist_percentage=astp, steal_percentage=stlp,
                                three_fg_attempt_rate=tpar, ft_attempt_rate=ftar,
                                block_percentage=blkp, turnover_percentage=tovp, usage_percentage=usgp,
                                offensive_win_shares=ows, defensive_win_shares=dws,
                                win_shares_per_48=wsp48, offensive_box_plus_minus=obpm, defensive_box_plus_minus=dbpm,
                                value_over_replacement_player=vorp)

    def _get_dob(self):
        date_str = self.get_item_prop("birthDate", attr="data-birth")
        return date.fromisoformat(date_str)

    def _get_draft_pick(self):
        element = self._parsed.find("strong", string=re.compile("Draft:"))
        if element:
            s = element.find_next_sibling(string=re.compile("overall"))
            if s:
                matches = re.findall(r"\d{1,2}[a-z]{1,3} overall", s.string)
                if matches:
                    return int("".join([c for c in matches[0] if c.isdigit()]))

    def _get_shooting_hand(self) -> str:
        return self.get_first_text_sibling("strong", "Shoots:")

    def _get_season_from_row(self, row):
        s = self.get_data_stat_in_element("season", row)
        return 0 if "Career" in s else int(s[0:4]) + 1

    def _get_salaries(self):
        table = self.get_commented_table_with_id("all_salaries")
        if not table:
            return []
        salaries = []
        for row in table.find("tbody").find_all("tr"):
            season = self.get_data_stat_in_element("season", row)
            team = self.get_data_stat_in_element("team_name", row, return_first_child=True)["href"]
            team_url = to_absolute_url(team)
            amount = int(self.get_data_stat_in_element("salary", row, "csk"))
            salaries.append(Salary(season=season, team=team_url, amount=amount))
        return salaries

    def _get_contract(self):
        table = self.get_commented_table_with_id("contracts_.*")
        if not table:
            return None
        rows = self.get_commented_table_with_id("contracts_.*").find_all("tr")
        if not len(rows):
            return None
        header_row = rows[0]
        if len(header_row.find_all()) == 1:
            return None
        contract_row = rows[1]
        years: List[ContractYear] = []
        seasons = [td.get_text() for td in header_row.find_all("th")]
        for td in [td for td in contract_row.find_all("td")[1:]]:
            season = len([sibling for sibling in td.previous_siblings if sibling.name == "td"])
            amount = int(re.sub("[$,]", "", td.get_text()))
            option_span = td.find("span")
            option = _get_contract_option(option_span.attrs["class"]) if option_span else None
            year = ContractYear(season=seasons[season], amount=amount, option=option)
            years.append(year)
        return Contract(years=years)
