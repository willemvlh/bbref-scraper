from bballer.scrapers.Search import Search
from bballer.scrapers.TeamScraper import TeamPageScraper


def get_by_name(name: str):
    result = Search.search_teams(name)
    if not len(result):
        return None
    url = result[0][-1]
    return TeamPageScraper(url).team()


def get_by_code(code: str):
    return TeamPageScraper(code).team()


def get_by_url(url: str):
    return TeamPageScraper(url).team()


def search(name: str):
    return Search.search_teams(name)
