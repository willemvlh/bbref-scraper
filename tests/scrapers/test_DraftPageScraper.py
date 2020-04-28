from bballer.models.draft import PlayerInDraft
from bballer.scrapers.DraftPageScraper import DraftPageScraper
from tests.scrapers.utils import get_resource


class TestDraftPageScraper:
    def test_scrape(self):
        iterator = DraftPageScraper(get_resource("draft_2003.html")).get_content()
        draft_pick = next(iterator)
        assert isinstance(draft_pick, PlayerInDraft)
        assert draft_pick.player.name == "LeBron James"
        assert draft_pick.college is None
        assert draft_pick.pick == 1
        assert draft_pick.years_in_league > 16
        assert draft_pick.team.name == "Cleveland Cavaliers"
