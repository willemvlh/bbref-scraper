import re
from typing import Tuple

from bballer.models.player import PlayerShell
from bballer.models.team import Team, TeamSeason
from bballer.scrapers.base import Scraper, get_data_stat_in_element
from bballer.scrapers.utilities import to_absolute_url


class TeamSeasonScraper(Scraper):
    def get_content(self):
        return self.get_roster()

    def __init__(self, code, year):
        url = f"https://www.basketball-reference.com/teams/{code}/{year}.html"
        super().__init__(url)

    def get_roster(self):
        table = self.find("table", id="roster")
        return [PlayerShell(name=get_data_stat_in_element("player", row),
                            url=to_absolute_url(row.find("td", attrs={"data-stat": "player"}).find("a").attrs["href"]))
                for row in table.find("tbody").find_all("tr")]


class TeamPageScraper(Scraper):
    def get_content(self):
        return self.team()

    def __init__(self, code_or_url: str):
        code_is_url = len(code_or_url) > 3
        url = code_or_url if code_is_url else f"https://www.basketball-reference.com/teams/{code_or_url}/"
        self.code = code_or_url if not code_is_url else None
        super().__init__(url)
        self._team_table = self.find("table", id=self._get_code())

    def team(self) -> Team:
        name = self._get_name()
        code = self._get_code()
        wins, losses = self._get_wins_and_losses()
        seasons = self._get_seasons()
        return Team(name=name, code=code, seasons=seasons, wins=wins, losses=losses)

    def _get_name(self):
        return self.get_item_prop("name", element="h1")

    def _get_wins_and_losses(self) -> Tuple[int, int]:
        record = self.get_first_text_sibling("strong", "Record:")
        wins_losses = re.findall(r"\d{1,5}-\d{1,5}", record)
        if not wins_losses:
            return 0, 0
        splits = map(int, wins_losses[0].split("-"))
        return tuple(splits)

    def _get_seasons(self):
        assert self._team_table is not None
        rows = self._team_table.find("tbody").find_all("tr")
        return list(reversed([self.parse_team_row(row) for row in rows]))

    def parse_team_row(self, row):
        season = get_data_stat_in_element("season", row)
        wins = get_data_stat_in_element("wins", row)
        losses = get_data_stat_in_element("losses", row)
        pace = get_data_stat_in_element("pace", row)
        rel_pace = get_data_stat_in_element("pace_rel", row)
        off_rtg = get_data_stat_in_element("off_rtg", row)
        off_rtg_rel = get_data_stat_in_element("off_rtg_rel", row)
        def_rtg = get_data_stat_in_element("def_rtg", row)
        def_rtg_rel = get_data_stat_in_element("def_rtg_rel", row)
        playoff_result = self._get_playoff_result_from_row(row)
        won_championship = playoff_result.lower() == "Won Finals".lower()
        made_playoffs = bool(playoff_result)
        return TeamSeason(season=season, wins=wins, losses=losses, pace=pace, rel_pace=rel_pace, rel_drtg=def_rtg_rel,
                          rel_ortg=off_rtg_rel, ortg=off_rtg, drtg=def_rtg, made_playoffs=made_playoffs,
                          won_championship=won_championship, playoff_result=playoff_result, _team_code=self._get_code())

    def _get_code(self):
        if not self.code:
            url = self.find("link", rel="canonical").attrs["href"]
            self.code = url.split("/")[-2]
        return self.code

    def _get_playoff_result_from_row(self, row):
        td = row.find("td", attrs={"data-stat": "rank_team_playoffs"})
        return td.find("strong").text if td.find("strong") else td.text
