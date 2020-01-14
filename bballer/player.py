from bballer.scrapers.PlayerPageScraper import PlayerPageScraper
from bballer.scrapers.Search import Search


def get_by_name(name: str):
    result = Search.search_players(name)
    if not len(result):
        return None
    url = result[0][-1]
    return PlayerPageScraper(url).player()


def search(term: str):
    return Search.search_players(term)


def get_by_url(url: str):
    return PlayerPageScraper(url).player()


def get_by_id(_id: str):
    url = f"https://www.basketball-reference.com/players/{_id[0]}/{_id}.html"
    return PlayerPageScraper(url).player()
