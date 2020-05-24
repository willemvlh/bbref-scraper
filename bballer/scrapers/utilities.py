def to_absolute_url(url: str) -> str:
    if url.startswith("http"):
        return url
    if url.startswith("/"):
        url = url[1:]
    return BASE_URL + url


def remove_year_from_team_url(url: str):
    # "/teams/MIN/2005.html" -> "/teams/MIN"
    url = "/".join(url.split("/")[0:2])
    return to_absolute_url(url)


BASE_URL = "https://www.basketball-reference.com/"
