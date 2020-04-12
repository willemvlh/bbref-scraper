def to_absolute_url(url: str) -> str:
    if url.startswith("http"):
        return url
    if url.startswith("/"):
        url = url[1:]
    return BASE_URL + url


BASE_URL = "https://www.basketball-reference.com/"
