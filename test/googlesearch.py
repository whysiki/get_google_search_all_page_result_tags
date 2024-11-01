import sys
import math
import re
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from random import choice
import requests
from typing import List, Optional, Tuple
from urllib.parse import quote
from pathlib import Path


def pure_html_remove_css_and_js(html: str) -> str:
    # soup = BeautifulSoup(html, "html.parser")
    # for script in soup(["script", "style"]):
    #     script.extract()
    # return soup.get_text()
    return re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.DOTALL)


class GoogleSearch:
    browser_agents_path = Path(__file__).parent / "browser_agents.txt"
    with open(browser_agents_path, "r") as file_handle:
        USER_AGENTS = file_handle.read().splitlines()
    SEARCH_URL = "https://google.com/search"
    RESULT_SELECTOR = "div.g"
    RESULT_SELECTOR_PAGE1 = "div.g>div>div[id][data-ved]"
    TOTAL_SELECTOR = "#result-stats"
    RESULTS_PER_PAGE = 10
    DEFAULT_HEADERS = {
        "User-Agent": choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.5",
    }

    def __init__(self):
        self.proxy = dict(http="http://localhost:62333", https="http://localhost:62333")
        self.session = requests.Session()
        self.session.proxies.update(self.proxy)
        self.session.headers.update(GoogleSearch.DEFAULT_HEADERS)

    def search(
        self,
        query: str,
        num_results: int = 10,
        prefetch_pages: bool = True,
        num_prefetch_threads: int = 10,
    ) -> "SearchResponse":
        """Perform the Google search.
        Parameters:
            query: String to search.
            num_results: Minimum number of results to stop search.
            prefetch_pages: Prefetch answered pages.
            num_prefetch_threads: Number of threads used to prefetch the pages.
        """
        search_results = []
        pages = int(math.ceil(num_results / float(GoogleSearch.RESULTS_PER_PAGE)))
        total = None
        thread_pool = None
        if prefetch_pages:
            thread_pool = ThreadPool(num_prefetch_threads)
        for i in range(pages):
            start = i * GoogleSearch.RESULTS_PER_PAGE
            response = self.session.get(
                f"{GoogleSearch.SEARCH_URL}?hl=en&q={quote(query)}&start={start}"
            )
            print(response.url)
            response.raise_for_status()
            re_text = response.text
            with open("response.html", "w", encoding="utf-8") as file_handle:
                file_handle.write(pure_html_remove_css_and_js(re_text))
            soup = BeautifulSoup(re_text, "html.parser")
            if total is None:
                total = self.extract_total_results(soup)
            selector = (
                GoogleSearch.RESULT_SELECTOR_PAGE1
                if i == 0
                else GoogleSearch.RESULT_SELECTOR
            )
            self.results = self.parse_results(soup.select(selector), i)
            search_results += self.results
            if prefetch_pages:
                thread_pool.map_async(SearchResult.get_text, self.results)
        if prefetch_pages:
            thread_pool.close()
            thread_pool.join()
        return SearchResponse(search_results, total)

    def extract_total_results(self, soup: BeautifulSoup) -> int:
        total_text = soup.select(GoogleSearch.TOTAL_SELECTOR)[0].get_text()
        total = int(
            re.sub(
                "[', ]", "", re.search(r"(([0-9]+[', ])*[0-9]+)", total_text).group(1)
            )
        )
        return total

    def parse_results(
        self, results: List[BeautifulSoup], page: int
    ) -> List["SearchResult"]:
        search_results = []
        for result in results:
            if page == 0:
                result = result.parent
            else:
                result = result.find("div")
            h3 = result.find("h3")
            if h3 is None:
                continue
            url = h3.parent["href"]
            title = h3.text
            search_results.append(SearchResult(title, url))
        return search_results


class SearchResponse:
    def __init__(self, results: List["SearchResult"], total: Optional[int]):
        self.results = results
        self.total = total


class SearchResult:
    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url
        self.__text = None
        self.__markup = None

    def get_text(self) -> str:
        if self.__text is None:
            soup = BeautifulSoup(self.get_markup(), "lxml")
            for junk in soup(["style", "script", "head", "title", "meta"]):
                junk.extract()
            self.__text = soup.get_text()
        return self.__text

    def get_markup(self) -> str:
        if self.__markup is None:
            response = requests.get(self.url, headers=GoogleSearch.DEFAULT_HEADERS)
            response.raise_for_status()
            self.__markup = response.text
        return self.__markup


if __name__ == "__main__":
    search = GoogleSearch()
    response = search.search("python")
    print(response.total)
