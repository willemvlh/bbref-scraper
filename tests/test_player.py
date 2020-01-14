from bballer import player
from bballer.models.player import Player


def test_get_by_name():
    anthony = player.get_by_name("Carmelo Anthony")
    assert anthony.name == "Carmelo Anthony"


def test_get_by_id():
    anthony = player.get_by_id("anthoca01")
    assert anthony.name == "Carmelo Anthony"


def test_search():
    result = player.search("LeBron James")
    for p in result:
        assert isinstance(p, tuple)

def test_get_by_url():
    anthony = player.get_by_url("https://www.basketball-reference.com/players/a/anthoca01.html")
    assert anthony.name == "Carmelo Anthony"