from typing import List
from bs4 import BeautifulSoup, Comment, NavigableString

from AdvancedStatLine import AdvancedStatLine
from Player import Player
from Statline import StatLine
import requests
import re
import jsonpickle
import os
import logging
import concurrent.futures


class Scraper:
    def __init__(self, url: str):
        self._url = url
        self._parsed = self._get_page()
        logging.debug(f"Scraping {url}")

    def _get_page(self):
        content = self._get_content()
        return BeautifulSoup(content, features="html.parser")

    def _get_content(self):
        if self._url.startswith("http"):
            logging.debug(f"Connecting to {self._url}")
            r = requests.get(self._url)
            r.raise_for_status()
            return r.content
        elif os.path.isfile(self._url):
            logging.debug(f"About to open {self._url}")
            with open(self._url, "r", encoding="utf-8") as f:
                logging.debug(f"Opened {self._url}")
                return f.read()
        else:
            raise ValueError


class BulkScraper:
    def __init__(self, urls):
        self._urls = urls
        self._processed = []

    def scrape_all(self, _max: int = None) -> List[Player]:
        urls = set(self._urls[0:_max] if _max else self._urls)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            players = executor.map(lambda u: PlayerPageScraper(u).player(), urls)
            return list(players)

    def serialize(self):
        jsonpickle.set_encoder_options(name="json", indent=1)
        return jsonpickle.encode(self._processed, unpicklable=False)


class PlayerPageScraper(Scraper):
    def __init__(self, url: str):
        super().__init__(url)
        self._reg_season_table = self.get_table_with_id("totals")
        self._playoff_table = self.get_table_with_id("playoffs_totals")

    def player(self) -> Player:
        id_ = self.get_id()
        name = self._get_name()
        seasons = self.get_regular_season_totals()
        playoffs = self.get_playoffs_totals()
        college = self.get_college()
        date_of_birth = self.get_dob()
        career_stats = self.get_career_stats()
        height, weight = self.get_physicals()
        draft_pick = self.get_draft_pick()
        positions = [season.position for season in seasons]
        position = max(positions, key=positions.count) if positions else None
        shooting_hand = self.get_shooting_hand()
        logging.debug(f"Processed {name}")
        return Player(id=id_, name=name, seasons=seasons, playoffs=playoffs, college=college,
                      date_of_birth=date_of_birth,
                      career_stats=career_stats, height=height, weight=weight, draft_pick=draft_pick, position=position,
                      shooting_hand=shooting_hand)

    def get_id(self):
        if os.path.isfile(self._url):
            return os.path.split(self._url)[-1].rstrip(".html")
        id_ = self._url.split("/")[-1].rstrip(".html")
        if not id_:
            raise ValueError("Player has no id!")
        return id_

    def get_physicals(self):
        return self._safe_get_item_prop("height"), int(self._safe_get_item_prop("weight").rstrip("lb"))

    def _get_name(self) -> str:
        return self._safe_get_item_prop("name", element="h1")

    def get_table_with_id(self, _id):
        # tables are embedded as comments in the document, so we have to fish
        comment = self._parsed.find(string=lambda x: isinstance(x, Comment) and f"id=\"{_id}\"" in x)
        if not comment:
            return
        parsed = BeautifulSoup(comment, features="html.parser")
        return parsed.find("table", id=_id)

    def get_career_stats(self):
        if self._reg_season_table:
            career_row = self._reg_season_table.find("th", string="Career").find_parent("tr")
            return self._parse_stats_from_row(career_row)

    def get_college(self):
        preceding_element = self._parsed.find("strong", text=re.compile("College:"))
        if preceding_element:
            return preceding_element.find_next_sibling("a").text

    def get_regular_season_totals(self):
        return self._get_totals(self._reg_season_table)

    def get_playoffs_totals(self):
        return self._get_totals(self._playoff_table)

    def _get_totals(self, table):
        if not table:
            return []
        rows = table.find_all("tr", class_="full_table")
        totals = []
        for row in rows:
            if self.get_stat_in_season("lg_id", row) == "NBA":
                season = self._parse_stats_from_row(row)
                totals.append(season)
        return totals

    def _parse_stats_from_row(self, row):
        season = self.get_stat_in_season("season", row)
        age = self.get_stat_in_season("age", row)
        team = self.get_stat_in_season("team_id", row)
        all_star = bool(row.find("span", class_="sr_star"))
        gamesPlayed = self.get_stat_in_season("g", row)
        gamesStarted = self.get_stat_in_season("gs", row)
        minutesPlayed = self.get_stat_in_season("mp", row)
        position = self.get_stat_in_season("pos", row)
        fg_made = self.get_stat_in_season("fg", row)
        fg_attempted = self.get_stat_in_season("fga", row)
        three_fg_made = self.get_stat_in_season("fg3", row)
        three_fg_attempted = self.get_stat_in_season("fg3a", row)
        two_fg_made = self.get_stat_in_season("fg2", row)
        two_fg_attempted = self.get_stat_in_season("fg2a", row)
        effective_fg_percentage = self.get_stat_in_season("efg_pct", row)
        free_throw_made = self.get_stat_in_season("ft", row)
        free_throw_attempted = self.get_stat_in_season("fta", row)
        offensive_rebounds = self.get_stat_in_season("orb", row)
        defensive_rebounds = self.get_stat_in_season("drb", row)
        assists = self.get_stat_in_season("ast", row)
        steals = self.get_stat_in_season("stl", row)
        blocks = self.get_stat_in_season("blk", row)
        turnovers = self.get_stat_in_season("tov", row)
        fouls = self.get_stat_in_season("pf", row)
        points = self.get_stat_in_season("pts", row)
        return StatLine(season=season, age=age, all_star=all_star, gamesPlayed=gamesPlayed, gamesStarted=gamesStarted,
                        minutesPlayed=minutesPlayed, team=team,
                        position=position, fg_made=fg_made, fg_attempted=fg_attempted, three_fg_made=three_fg_made,
                        three_fg_attempted=three_fg_attempted, two_fg_made=two_fg_made,
                        two_fg_attempted=two_fg_attempted, effective_fg_percentage=effective_fg_percentage,
                        free_throw_made=free_throw_made, free_throw_attempted=free_throw_attempted,
                        offensive_rebounds=offensive_rebounds, defensive_rebounds=defensive_rebounds,
                        assists=assists, steals=steals, blocks=blocks, turnovers=turnovers, fouls=fouls, points=points)

    def _parse_stats_from_advanced_row(self, row):

        return AdvancedStatLine()

    def _safe_get_item_prop(self, prop, attr=None, element=None):
        el = self._parsed.find(element, attrs={"itemprop": prop})
        if el and attr and el.attrs[attr]:
            return el.attrs[attr]
        if el:
            return el.text
        return None

    def get_stat_in_season(self, stat_name, element):
        val = element.find(attrs={"data-stat": stat_name})
        if not val:
            return None
        val: str = val.text
        try:
            if val.startswith("."):
                return float(val)
            return int(val)
        except ValueError:
            return val

    def get_dob(self):
        return self._safe_get_item_prop("birthDate", attr="data-birth")

    def get_draft_pick(self):
        element = self._parsed.find("strong", string=re.compile("Draft:"))
        if element:
            s = element.find_next_sibling(string=re.compile("overall"))
            if s:
                matches = re.findall(r"\d{1,2}[a-z]{1,3} overall", s.string)
                if matches:
                    return int("".join([c for c in matches[0] if c.isdigit()]))

    def get_shooting_hand(self) -> str:
        element = self._parsed.find("strong", string=re.compile("Shoots:"))
        if element:
            return element.find_next_sibling(string=lambda x: isinstance(x, NavigableString)).strip()


class PlayerListScraper(Scraper):
    def __init__(self, url: str):
        super().__init__(url)

    def get_player_urls(self):
        cells = self._parsed.find_all("th", {"data-stat": "player", "scope": "row"})
        return ["https://www.basketball-reference.com" + cell.find_next("a").attrs["href"] for cell in cells]


class TotalMinutesScraper(Scraper):
    def __init__(self, year: int):
        url = f"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html"
        super().__init__(url)

    def get_player_urls(self):
        cells = self._parsed.find_all("td", {"data-stat": "player"})
        return ["https://www.basketball-reference.com" + cell.find_next("a").attrs["href"] for cell in cells]
