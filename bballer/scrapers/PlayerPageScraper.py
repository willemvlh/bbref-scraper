import logging
import os
import re
from datetime import date
from typing import List, Optional, Type

from bballer.models.advanced_stats import AdvancedStatLine
from bballer.models.player import Salary, Contract, ContractYear, DraftPick, Player
from bballer.models.stats import StatLine, PlayoffStatLine, ShootingStatLine, ShootingByDistance
from bballer.models.team import TeamShell
from bballer.scrapers.base import Scraper, get_data_stat_in_element
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
        playoffs = self._get_playoffs_totals()
        college = self._get_college()
        date_of_birth = self._get_dob()
        career_stats = self._get_career_stats()
        height, weight = self._get_physical()
        draft_pick = self._get_draft_pick()
        positions = [season.position for season in list(self._get_regular_season_totals())]
        position = max(positions, key=positions.count) if positions else None
        seasons = self._get_regular_season_totals()  # recalculate to reset the generator
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
        for el in self._get_totals(self._reg_season_table):
            yield el

    def _get_playoffs_totals(self):
        return self._get_totals(self._playoff_table, PlayoffStatLine)

    def _get_totals(self, table, statline_type=StatLine):
        if not table:
            yield None
        rows = table.find_all("tr", class_="full_table")
        for row in rows:
            if get_data_stat_in_element("lg_id", row) == "NBA":
                yield self._parse_stats_from_row(row, statline_type)

    def _parse_stats_from_row(self, row, statline_type: Type[StatLine] = StatLine):
        season = self._get_season_from_row(row)
        age = get_data_stat_in_element("age", row)
        team = get_data_stat_in_element("team_id", row)
        all_star = bool(row.find("span", class_="sr_star"))
        games_played = get_data_stat_in_element("g", row)
        games_started = get_data_stat_in_element("gs", row)
        minutes_played = get_data_stat_in_element("mp", row)
        position = get_data_stat_in_element("pos", row)
        fg_made = get_data_stat_in_element("fg", row)
        fg_attempted = get_data_stat_in_element("fga", row)
        three_fg_made = get_data_stat_in_element("fg3", row)
        three_fg_attempted = get_data_stat_in_element("fg3a", row)
        two_fg_made = get_data_stat_in_element("fg2", row)
        two_fg_attempted = get_data_stat_in_element("fg2a", row)
        effective_fg_percentage = get_data_stat_in_element("efg_pct", row)
        free_throw_made = get_data_stat_in_element("ft", row)
        free_throw_attempted = get_data_stat_in_element("fta", row)
        offensive_rebounds = get_data_stat_in_element("orb", row)
        defensive_rebounds = get_data_stat_in_element("drb", row)
        assists = get_data_stat_in_element("ast", row)
        steals = get_data_stat_in_element("stl", row)
        blocks = get_data_stat_in_element("blk", row)
        turnovers = get_data_stat_in_element("tov", row)
        fouls = get_data_stat_in_element("pf", row)
        points = get_data_stat_in_element("pts", row)
        sl = ShootingDataScraper(self.get_commented_table_with_id(statline_type.shooting_data_table_id))
        shooting_data = sl.get_shooting_data(season)
        statline = statline_type(season=season, age=age, all_star=all_star, games_played=games_played,
                                 games_started=games_started,
                                 minutes_played=minutes_played, team=team,
                                 position=position, fg_made=fg_made, fg_attempted=fg_attempted,
                                 three_fg_made=three_fg_made,
                                 three_fg_attempted=three_fg_attempted, two_fg_made=two_fg_made,
                                 two_fg_attempted=two_fg_attempted, effective_fg_percentage=effective_fg_percentage,
                                 ft_made=free_throw_made, ft_attempted=free_throw_attempted,
                                 offensive_rebounds=offensive_rebounds, defensive_rebounds=defensive_rebounds,
                                 assists=assists, steals=steals, blocks=blocks, turnovers=turnovers, fouls=fouls,
                                 points=points, _player_url=self._url, shooting_data=shooting_data)
        advanced_statline_rows = [tr for tr in self._advanced_table.find_all("tr", class_="full_table") if
                                  self._get_season_from_row(tr) == season]
        if advanced_statline_rows:
            advanced_statline = self._parse_stats_from_advanced_row(advanced_statline_rows[0], statline)
            statline.advanced = advanced_statline
        return statline

    def _parse_stats_from_advanced_row(self, row, season):
        per = get_data_stat_in_element("per", row)
        tsp = get_data_stat_in_element("ts_pct", row)
        orb = get_data_stat_in_element("orb_pct", row)
        tpar = get_data_stat_in_element("fg3a_per_fga_pct", row)
        ftar = get_data_stat_in_element("fta_per_fga_pct", row)
        drb = get_data_stat_in_element("drb_pct", row)
        trb = get_data_stat_in_element("trb_pct", row)
        astp = get_data_stat_in_element("ast_pct", row)
        stlp = get_data_stat_in_element("stl_pct", row)
        blkp = get_data_stat_in_element("blk_pct", row)
        tovp = get_data_stat_in_element("tov_pct", row)
        usgp = get_data_stat_in_element("usg_pct", row)
        ows = get_data_stat_in_element("ows", row)
        dws = get_data_stat_in_element("dws", row)
        wsp48 = get_data_stat_in_element("ws_per_48", row)
        obpm = get_data_stat_in_element("obpm", row)
        dbpm = get_data_stat_in_element("dbpm", row)
        vorp = get_data_stat_in_element("vorp", row)

        return AdvancedStatLine(basic_stats=season, player_efficiency_rating=per, true_shooting_percentage=tsp,
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
            team = element.find_next_sibling("a")
            url = team.attrs["href"].rstrip("/draft.html")
            team_shell = TeamShell(name=team.get_text(), url=to_absolute_url(url))
            txt = element.find_next_sibling(string=re.compile("overall"))
            year = int(team.find_next_sibling("a").get_text()[0:4])
            if txt:
                numbers = [int(x) for x in re.findall("\\d{1,2}", txt)]
                assert len(numbers) == 3
                return DraftPick(round=numbers[0], pick=numbers[1], overall=numbers[2], team=team_shell, year=year)
            return DraftPick(round=None, pick=None, overall=None, team=team_shell, year=year)

    def _get_shooting_hand(self) -> str:
        return self.get_first_text_sibling("strong", "Shoots:")

    def _get_season_from_row(self, row):
        s = get_data_stat_in_element("season", row)
        return 0 if "Career" in s else int(s[0:4]) + 1

    def _get_salaries(self):
        table = self.get_commented_table_with_id("all_salaries")
        if not table:
            return []
        salaries = []
        for row in table.find("tbody").find_all("tr"):
            season = get_data_stat_in_element("season", row)
            team = get_data_stat_in_element("team_name", row, return_first_child=True)["href"]
            team_url = to_absolute_url(team)
            amount = int(get_data_stat_in_element("salary", row, "csk"))
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


class ShootingDataScraper:
    def __init__(self, table):
        self.table = table

    def get_shooting_data(self, season):
        table = self.table
        if not table:
            return None
        if season == 0:  # Career stats
            row = table.find("tfoot").find("tr")
        else:
            row = table.find("tr", id=re.compile(f"{season}$"))
            if not row:
                return None
        return self._parse_stats_from_shooting_row(row)

    def _parse_stats_from_shooting_row(self, row):
        sd = ShootingStatLine()
        sd.fga_by_distance = self.get_fga_by_distance(row)
        sd.fgp_by_distance = self.get_fgp_by_distance(row)
        sd.avg_distance = get_data_stat_in_element("avg_dist", row)
        sd.two_point_fga_assisted = get_data_stat_in_element("fg2_pct_ast", row)
        sd.dunks_fga = get_data_stat_in_element("pct_fg2_dunk", row)
        sd.dunks_made = get_data_stat_in_element("fg2_dunk", row)
        sd.three_point_fga_assisted = get_data_stat_in_element("fg3_pct_ast", row)
        sd.corner_three_point_fga = get_data_stat_in_element("pct_fg3a_corner", row)
        sd.corner_three_point_fgp = get_data_stat_in_element("fg3_pct_corner", row)
        sd.heaves_attempted = get_data_stat_in_element("fg3a_heave", row)
        sd.heaves_made = get_data_stat_in_element("fg3_heave", row)
        return sd

    def get_fga_by_distance(self, row):
        two_point = get_data_stat_in_element("fg2a_pct_fga", row)
        zero_three = get_data_stat_in_element("pct_fga_00_03", row)
        three_ten = get_data_stat_in_element("pct_fga_03_10", row)
        ten_sixteen = get_data_stat_in_element("pct_fga_10_16", row)
        sixteen_xx = get_data_stat_in_element("pct_fga_16_xx", row)
        three_point = get_data_stat_in_element("fg3a_pct_fga", row)
        return ShootingByDistance(two_point, zero_three, three_ten, ten_sixteen, sixteen_xx, three_point)

    def get_fgp_by_distance(self, row):
        two_point = get_data_stat_in_element("fg2_pct", row)
        zero_three = get_data_stat_in_element("fg_pct_00_03", row)
        three_ten = get_data_stat_in_element("fg_pct_03_10", row)
        ten_sixteen = get_data_stat_in_element("fg_pct_10_16", row)
        sixteen_xx = get_data_stat_in_element("fg_pct_16_xx", row)
        three_point = get_data_stat_in_element("fg3_pct", row)
        return ShootingByDistance(two_point, zero_three, three_ten, ten_sixteen, sixteen_xx, three_point)
