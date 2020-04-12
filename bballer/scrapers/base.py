import logging
import os
import re

import requests
from bs4 import BeautifulSoup, NavigableString, Comment


class Scraper:
    def __init__(self, url: str):
        self._url = url
        self._parsed = self._get_page()
        logging.debug(f"Scraping {url}")

    def get_content(self):
        raise NotImplementedError
        # TODO: implement method in subclasses that returns the scraped and processed object

    def _get_page(self):
        content = self._get_content()
        return BeautifulSoup(content, features="html.parser")

    def find(self, element, **kwargs):
        return self._parsed.find(element, **kwargs)

    def find_all(self, element, **kwargs):
        self._parsed.find_all("div", class_="score")
        return self._parsed.find_all(element, **kwargs)

    def _get_content(self):
        if self._url.startswith("http"):
            logging.debug(f"Connecting to {self._url}")
            r = requests.get(self._url)
            r.raise_for_status()
            return r.content
        elif os.path.isfile(self._url):
            logging.debug(f"About to open {self._url}")
            with open(self._url, "r", encoding="utf-8") as f:
                logging.debug(f"Opened {self._url}")
                return f.read()
        else:
            raise ValueError

    def get_data_stat_in_element(self, stat_name, element, attr=None):
        val = element.find(attrs={"data-stat": stat_name})
        if not val:
            return None
        if attr:
            val = val.attrs[attr]
        else:
            val = val.text if not val.find("a") else val.find("a").text
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return val

    def safe_get_item_prop(self, prop, attr=None, element=None):
        el = self._parsed.find(element, attrs={"itemprop": prop})
        if el and attr and el.attrs[attr]:
            return el.attrs[attr].strip()
        if el:
            return el.text.strip()
        return None

    def get_text_sibling(self, tag_name: str, tag_value: str):
        element = self._parsed.find(tag_name, string=re.compile(tag_value))
        if element:
            return element.find_next_sibling(string=lambda x: isinstance(x, NavigableString)).strip()

    def get_commented_table_with_id(self, _id):
        # tables are embedded as comments in the document, so we have to fish
        comment = self._parsed.find(string=lambda x: isinstance(x, Comment) and f"id=\"{_id}\"" in x)
        if not comment:
            return
        parsed = BeautifulSoup(comment, features="html.parser")
        return parsed.find("table", id=_id)
