from unittest.case import TestCase

from bballer.scrapers.search import Search


class TestSearch(TestCase):
    def test_search_players(self):
        results = Search.search_players("Kobe")
        assert len(results) == 4
        assert 'Kobe Bryant (1997-2016)' in [_tuple[0] for _tuple in results]
        assert all([_tuple[1].startswith("https://www.basketball-reference.com/players/") for _tuple in results])

    def test_search_players_redirect(self):
        # sometimes the search engine does not return a result page, but redirects automatically
        results = Search.search_players("LeBron")
        assert isinstance(results, list)
        print(results)

    def test_team_search(self):
        results = Search.search_teams("Bobcats")
        assert len(results) == 1
        team, url = results[0]
        assert "Bobcats" in team
        assert url.startswith("http")