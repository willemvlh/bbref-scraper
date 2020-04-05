from bballer import team


def test_get_by_name():
    t = team.get_by_name("Cleveland Cavaliers")
    assert t.name == "Cleveland Cavaliers"

def test_get_by_name_wrong():
    t = team.get_by_name("blabla")
    assert(t is None)


def test_get_by_code():
    t = team.get_by_code("CLE")
    assert t.name == "Cleveland Cavaliers"


def test_get_by_url():
    t = team.get_by_url("https://www.basketball-reference.com/teams/CLE/")
    assert t.name == "Cleveland Cavaliers"


def test_search():
    t = team.search("Cavaliers")
    for team_ in t:
        assert isinstance(team_, tuple)
