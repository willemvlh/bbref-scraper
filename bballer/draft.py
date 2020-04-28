from typing import Iterator

from bballer.models.draft import PlayerInDraft
from bballer.scrapers.DraftPageScraper import DraftPageScraper


def get_url(year) -> str:
    return f"https://www.basketball-reference.com/draft/NBA_{year}.html"


def year(year: int) -> Iterator[PlayerInDraft]:
    return DraftPageScraper(get_url(year)).get_content()
