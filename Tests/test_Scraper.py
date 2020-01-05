from unittest import TestCase
from Scraper import *
from Statline import StatLine
from pathlib import Path


def assert_equal(first, second):
    if first != second:
        raise AssertionError(f"AssertionError: {first} does not equal {second}")


def get_resource(fn):
    return str(Path(__file__).parent.joinpath("resources").joinpath(fn).absolute())


class TestScraper:
    carmelo_anthony = PlayerPageScraper(get_resource("carmelo_anthony.html"))
    lebron_james = PlayerPageScraper(get_resource("lebron_james.html"))
    julius_erving = PlayerPageScraper(get_resource("julius_erving.html"))
    ben_wallace = PlayerPageScraper(get_resource("ben_wallace.html"))

    def test_equality(self):
        this_player = self.carmelo_anthony.player()
        assert (this_player != self.lebron_james.player())
        _set = {this_player, this_player}
        assert len(_set) == 1

    def test__get_name(self):
        assert self.carmelo_anthony._get_name() == "Carmelo Anthony"

    def test_get_dob(self):
        assert self.carmelo_anthony.get_dob() == "1984-05-29"

    def test_get_career_stats(self):
        stats = self.carmelo_anthony.get_career_stats()
        assert isinstance(stats, StatLine)
        assert int(stats.gamesStarted) > 1000

    def test_get_id(self):
        assert self.carmelo_anthony.get_id() == "carmelo_anthony"

    def test_get_shooting_hand(self):
        assert self.carmelo_anthony.get_shooting_hand() == "Right"

    def test_get_college(self):
        assert self.carmelo_anthony.get_college() == "Syracuse"
        assert self.lebron_james.get_college() is None

    def test_player(self):
        player = self.carmelo_anthony.player()
        assert len(player.seasons) > 10
        rookie_season = player.seasons[0]
        assert rookie_season.position == "SF"
        assert_equal(rookie_season.season, "2003-04")
        assert_equal(rookie_season.gamesStarted, 82)
        assert_equal(rookie_season.gamesPlayed, 82)
        assert_equal(rookie_season.minutesPlayed, 2995)
        assert_equal(rookie_season.fg_attempted, 1465)
        assert_equal(rookie_season.fg_made, 624)
        assert_equal(rookie_season.three_fg_made, 69)
        assert_equal(rookie_season.three_fg_attempted, 214)
        assert_equal(rookie_season.two_fg_attempted, 1251)
        assert_equal(rookie_season.two_fg_made, 555)
        assert_equal(rookie_season.effective_fg_percentage, 0.449)
        assert_equal(rookie_season.free_throw_made, 408)
        assert_equal(rookie_season.free_throw_attempted, 525)
        assert_equal(rookie_season.offensive_rebounds, 183)
        assert_equal(rookie_season.defensive_rebounds, 315)
        assert_equal(rookie_season.rebounds, 498)
        assert_equal(rookie_season.all_star, False)
        assert_equal(rookie_season.assists, 227)
        assert_equal(rookie_season.blocks, 41)
        assert_equal(rookie_season.turnovers, 247)
        assert_equal(rookie_season.steals, 97)
        assert_equal(rookie_season.fouls, 225)
        assert_equal(rookie_season.points, 1725)

    def test_advanced_stats(self):
        player = self.carmelo_anthony.player()
        s = player.seasons[0]
        assert s.advanced.astp == 13.8

    def test_seasons(self):
        seasons = self.julius_erving.get_regular_season_totals()
        assert len(seasons) == 11  # ABA seasons must be discarded

    def test_get_physicals(self):
        assert self.carmelo_anthony.get_physicals() == ("6-8", 240)

    def test_get_draft_pick(self):
        assert self.carmelo_anthony.get_draft_pick() == 3
        assert self.ben_wallace.get_draft_pick() is None

    def test_all_star(self):
        assert len([season for season in self.julius_erving.get_regular_season_totals() if season.all_star]) == 11

    def test_get_playoff_totals(self):
        assert len(self.julius_erving.get_playoffs_totals()) == 11
        assert sum([season.points for season in self.julius_erving.get_playoffs_totals()]) == 3088


class TestPlayerListScraper(TestCase):

    def test_scrape(self):
        s = PlayerListScraper(get_resource("w.html"))
        urls = s.get_player_urls()
        assert len(urls) == 364
        assert all([url.startswith("https://www.basketball-reference.com/players/") for url in urls])



class TestTotalMinutesListScraper(TestCase):
    def test_scrape(self):
        s = TotalMinutesScraper(2000)
        urls = s.get_player_urls()
        assert len(urls) > 10
        assert all([url.startswith("https://www.basketball-reference.com/players/") for url in urls])


class TestBulkScraper(TestCase):

    def test_scrape(self):
        logging.getLogger().setLevel(logging.DEBUG)
        bulk_scr = BulkScraper(map(get_resource, ["lebron_james.html", "carmelo_anthony.html"]))
        processed = bulk_scr.scrape_all()
        assert_equal(len(processed), 2)
        assert "Carmelo Anthony" in [p.name for p in processed]

    def test_double_scrape(self):
        bulk_scr = BulkScraper(map(get_resource, ["lebron_james.html", "lebron_james.html"]))
        players = bulk_scr.scrape_all()
        assert len(players) == 1


