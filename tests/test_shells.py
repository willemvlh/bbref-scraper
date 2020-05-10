from bballer.models.player import PlayerShell
from bballer.models.team import TeamShell
from tests.scrapers.utils import get_resource


class TestPlayerShell:
    def test_as_player(self):
        shell = PlayerShell("LeBron James", get_resource("lebron_james.html"))
        assert repr(shell) == "LeBron James"
        player = shell.as_player()
        assert player.name == "LeBron James"


class TestTeamShell:
    def test_as_team(self):
        shell = TeamShell("Cleveland Cavaliers", get_resource("cavs.html"))
        assert repr(shell) == "Cleveland Cavaliers"
        team = shell.as_team()
        assert team.name == "Cleveland Cavaliers"
