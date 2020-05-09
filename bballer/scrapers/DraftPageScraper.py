from typing import Iterator

from bballer.models.PlayerShell import PlayerShell
from bballer.models.draft import PlayerInDraft
from bballer.models.team import TeamShell
from bballer.scrapers.base import Scraper, get_data_stat_in_element
from bballer.scrapers.utilities import to_absolute_url


class DraftPageScraper(Scraper):

    def get_content(self) -> Iterator[PlayerInDraft]:
        table = self._parsed.find("table", id="stats")
        for tr in table.find("tbody").find_all("tr"):
            yield self._parse_row(tr)

    def _parse_row(self, tr) -> PlayerInDraft:
        link = get_data_stat_in_element("player", tr, return_first_child=True)
        player = PlayerShell(name=link.get_text(), url=to_absolute_url(link.attrs["href"]))
        pick = get_data_stat_in_element("pick_overall", tr, "csk")
        college = get_data_stat_in_element("college_name", tr, "csk")
        college = college if college != "Zzz" else None  # remarkable placeholder
        years = int(get_data_stat_in_element("seasons", tr))
        team_link = get_data_stat_in_element("team_id", tr, return_first_child=True)
        team = TeamShell(name=team_link.attrs["title"],
                         url=to_absolute_url(team_link.attrs["href"].rstrip("/draft.html")))
        return PlayerInDraft(player=player, team=team, pick=pick, college=college, years_in_league=years)
