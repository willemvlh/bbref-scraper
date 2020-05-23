from bballer.scrapers.Search import Search
from bballer.scrapers.TeamScraper import TeamPageScraper


def get_by_name(name: str):
    result = Search.search_teams(name)
    if not result:
        return None
    url = result[0][-1]
    return TeamPageScraper(url).get_content()


def get_by_code(code: str):
    return TeamPageScraper(code).get_content()


def get_by_url(url: str):
    return TeamPageScraper(url).get_content()


def search(name: str):
    return Search.search_teams(name)
