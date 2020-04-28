from bballer import draft
from bballer.models.draft import PlayerInDraft


class TestDraft:
    def test_draft(self):
        d = draft.year(2003)
        draft_pick = next(d)
        assert isinstance(draft_pick, PlayerInDraft)
        assert draft_pick.player.name == "LeBron James"
        assert draft_pick.college is None
        assert draft_pick.pick == 1
        assert draft_pick.years_in_league > 16
        assert draft_pick.team.name == "Cleveland Cavaliers"
