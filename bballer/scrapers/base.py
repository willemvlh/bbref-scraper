import logging
import os
import re
from typing import Union

from bs4 import BeautifulSoup, NavigableString, Comment, PageElement

from bballer.scrapers.download import Download


class Scraper:
    """
    Base class for each scraper.
    """

    def __init__(self, url: str):
        self._url = url
        self._parsed = self._get_page()
        logging.debug(f"Scraping {url}")

    def get_content(self):
        raise NotImplementedError

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
            return Download.download(self._url)
        elif os.path.isfile(self._url):
            logging.debug(f"About to open {self._url}")
            with open(self._url, "r", encoding="utf-8") as f:
                logging.debug(f"Opened {self._url}")
                return f.read()
        else:
            raise ValueError

    def get_data_stat_in_element(self, stat_name, element, attr=None, return_first_child=False) -> Union[
        PageElement, str, int, float, None]:

        # this should be split up in two functions really
        """Returns the text value of a child of {element} which has an attribute "data-stat" with value {stat_name}.
        If {attr} is not None, it will return the value of the attribute with name {attr}.

        :param stat_name: The value of the "data-stat" attribute.
        :param element: The element which contains the searched child element.
        :param attr: An optional attribute name of which the value should be returned.
        :param return_first_child: Return the first child of the found element, rather than the text value
        :return: A string or None.
        """
        if attr and return_first_child:
            raise ValueError("Arguments attr and return_first_child are mutually exclusive.")
        val = element.find(attrs={"data-stat": stat_name})
        if not val:
            return None
        if attr:
            val = val.attrs[attr]
        elif return_first_child:
            return val.find()
        else:
            val = val.text if not val.find("a") else val.find("a").text
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return val

    def get_item_prop(self, prop: str, attr=None, element=None):
        """
        Returns the text value of a child of {element} which has an attribute "itemprop" with value {attr}.
        @param prop: the value of the itemprop attribute
        @param attr: if specified, returns the value of the attribute with this name instead of the text value of the
        element.
        @param element: if specified, the name of the element.
        @return: the text value of the matching element or None.
        """
        # todo: refactor to bring in line with get_data_stat_in_element
        el = self._parsed.find(element, attrs={"itemprop": prop})
        if el and attr and el.attrs[attr]:
            return el.attrs[attr].strip()
        if el:
            return el.text.strip()
        return None

    def get_first_text_sibling(self, tag_name: str, tag_value: str):
        """
        Returns the first text node sibling of a specified element.
        @param tag_name: the name of the element.
        @param tag_value: a regular expression matching the text value of the element.
        @return:
        """
        element = self._parsed.find(tag_name, string=re.compile(tag_value))
        if element:
            return element.find_next_sibling(string=lambda x: isinstance(x, NavigableString)).strip()

    def get_commented_table_with_id(self, id_regex):
        """
        Find table element embedded in an HTML comment.
        @param id_regex: a regular expression matching the id of the table element.
        @return: the table element
        """
        # tables are embedded as comments in the document, so we have to fish
        comment = self._parsed.find(string=lambda x: isinstance(x, Comment) and re.search(f"id=\"{id_regex}\"", x))
        if not comment:
            return
        parsed = BeautifulSoup(comment, features="html.parser")
        return parsed.find("table", id=re.compile(id_regex))
