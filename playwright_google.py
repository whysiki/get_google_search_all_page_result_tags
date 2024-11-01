import asyncio
import httpx
from bs4 import BeautifulSoup
from pathlib import Path
from rich.console import Console
import re
from functools import wraps, lru_cache
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from loguru import logger
from time import time
from fake_useragent import UserAgent
from rich import print
from playwright.async_api import Route, Request, Page, BrowserContext
from typing import List, Dict
import random

logger.add(
    "log/{time:YYYY-MM-DD}.log",
    rotation="1 day",
    format="{time} {level} {message}",
    mode="a",
    level="SUCCESS",
)


def pure_html_remove_css_and_js(html: str) -> str:
    return re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.DOTALL)


def save_html(
    html: str, filename: str | Path, write_mode: str = "w", remove_js_css: bool = False
) -> None:
    assert isinstance(filename, (str, Path)), "Filename must be a string or Path object"
    save_path = Path(filename) if isinstance(filename, str) else filename
    assert save_path.suffix == ".html", "Filename must have .html extension"
    if not save_path.parent.exists():
        save_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Creating directory {save_path.parent}")
    with open(filename, write_mode, encoding="utf-8") as file:
        if remove_js_css:
            file.write(pure_html_remove_css_and_js(html))
        else:
            file.write(html)


async def handle_route_banimg_and_media(route: Route, request: Request) -> None:
    if request.resource_type in ["image", "media"]:
        await route.abort()
        logger.debug(f"Abort: {request.url}")
    else:
        await route.continue_()


def retry(retry_times: int = 3, delay_range: tuple = (1, 3)):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(retry_times):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error: {e}, retrying {i + 1}/{retry_times}")
                    await asyncio.sleep(random.uniform(*delay_range))
            return 1

        return wrapper

    return decorator


def semaphore_decorator(semaphore: asyncio.Semaphore = asyncio.Semaphore(3)):
    def semaphore_decorator_wrapper(func):
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return semaphore_decorator_wrapper


class GoogleSearch:
    def __init__(self) -> None:
        self.base_url = "https://google.com/search"
        self.proxy_url = "http://localhost:62333"  # if get none, use your own proxy
        self.proxies_dict = dict(http=self.proxy_url, https=self.proxy_url)
        self.result_tag_set: set = set()
        self.search_url: str = ""
        self.search_query: str = ""
        self.page_url_dict: Dict[str, str] = {}
        self.error_path = Path("error") / f"{int(time())}"
        self.test_path = Path("data") / f"{int(time())}"
        self.limit_page_range: tuple = None  # [1, 10]

    @property
    def sorted_page_url_dict_items(self) -> List[tuple]:
        return sorted(self.page_url_dict.items(), key=lambda x: int(x[0]))

    async def search(
        self,
        search_query: str,
        limit_page_range: tuple[int, int] = None,
    ) -> None:
        self.search_url = f"{self.base_url}?hl=en&q={search_query}"
        self.search_query = search_query
        safe_search_query = re.sub(r'[\/:*?"<>|]', "_", search_query).replace(" ", "_")
        self.error_path = self.error_path / safe_search_query
        self.test_path = self.test_path / safe_search_query
        if limit_page_range:
            assert isinstance(limit_page_range, tuple), "limit_page_range must be tuple"
            assert len(limit_page_range) == 2, "limit_page_range must have 2 elements"
            assert (
                limit_page_range[0] < limit_page_range[1]
            ), "First element must be less than second element"
            self.limit_page_range = limit_page_range
        else:
            self.limit_page_range = None
        await self.get_pages()

    async def get_pages(self):
        async with async_playwright() as p:
            async with await p.chromium.launch(
                proxy={"server": next(iter(self.proxies_dict.values()))},
                headless=True,
                args=["--incognito", "--disable-gpu"],
            ) as browser:
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto(self.search_url, wait_until="domcontentloaded")
                logger.debug(f"Search url: {self.search_url}")
                html_text = await page.content()
                currentpage_num: int = self.process_html(html_text)  # 1
                logger.debug(f"Inital current page: {currentpage_num}")
                assert isinstance(currentpage_num, int), "currentpage_num must be int"
                processed_page_set: set = {currentpage_num}
                await page.close()
                while greater_than_currentpagenum_urls := [
                    url
                    for num, url in self.page_url_dict.items()
                    if int(num) not in processed_page_set
                    and (
                        not self.limit_page_range  # Not None = True
                        or (
                            int(num) <= self.limit_page_range[1]
                            and int(num) >= self.limit_page_range[0]
                        )
                    )
                ]:
                    for future in asyncio.as_completed(
                        [
                            self.get_page(context, url)
                            for url in greater_than_currentpagenum_urls
                        ]
                    ):
                        processed_page_num = await future
                        processed_page_set.add(processed_page_num)
                        if processed_page_num:
                            logger.debug(f"Processed page: {processed_page_num}")
                        else:
                            logger.error(f"Error Processed page: {processed_page_num}")

    @retry(retry_times=5, delay_range=(2, 5))
    @semaphore_decorator(
        semaphore=asyncio.Semaphore(3)
    )  # 3 concurrent requests, if too many async requests, it will be blocked
    async def get_page(self, context: BrowserContext, url: str) -> int:
        try:
            page = await context.new_page()
            page.on("route", handle_route_banimg_and_media)
            await page.goto(url, wait_until="domcontentloaded")
            html_text = await page.content()
            processed_page_num = self.process_html(html_text)
            assert isinstance(processed_page_num, int), "processed_page_num must be int"
            return processed_page_num
        finally:
            await page.close()

    def process_html(self, html_text: str) -> int:
        soup = BeautifulSoup(html_text, "html.parser")
        searched_result_tag_set = soup.select("#rso > div")
        current_page_tag = soup.select_one("tr > td.YyVfkd.NKTSme")
        if current_page_tag is None:
            logger.error(
                "No current page tag found, maybe blocked, you can try again later or switch proxy"
            )
            save_html(
                html_text,
                self.error_path
                / f"error_response_{int(time())}_{self.search_query}_no_current_page.html",
            )
            # print(f"[bold red][/bold red]")
            html_plain_text = soup.select_one("body").text
            if html_plain_text:
                print(f"[bold red]Error: {html_plain_text}[/bold red]")
            return 1
        current_page: str = current_page_tag.text
        logger.debug(f"Current page: {current_page}")
        if searched_result_tag_set:
            old_result_tag_set_len = len(self.result_tag_set)
            self.result_tag_set.update(searched_result_tag_set)
            new_result_tag_set_len = len(self.result_tag_set)
            logger.success(
                f"Added {new_result_tag_set_len - old_result_tag_set_len} results"
            )
            save_html(
                "\n".join([tag.prettify() for tag in searched_result_tag_set]),
                self.test_path
                / Path(f"search_{self.search_query}_page_{current_page}.html"),
            )
            for index, tag in enumerate(searched_result_tag_set):
                text = tag.text
                if text:
                    print(
                        f"[bold green]Page {current_page}[/bold green] Result {index + 1}:\n {text}"
                    )
        else:
            save_html(
                html_text,
                self.error_path
                / f"error_response_{self.search_query}_page_{current_page}.html",
            )
            logger.error("No results found")

        page_tag_set = soup.select("tr > td.NKTSme")
        logger.debug(f"Page tag set length: {len(page_tag_set)}")
        page_url_dict = {}
        page_url_dict = {
            tag.text: (
                a_tag["href"].strip()
                if a_tag["href"].startswith("http")
                else f"https://google.com{a_tag['href'].strip()}"
            )
            for tag in page_tag_set
            if (a_tag := tag.a)
        }
        self.page_url_dict.update(page_url_dict)
        logger.debug(f"updated {len(page_url_dict)} page urls dict")

        return int(current_page) if isinstance(current_page, str) else current_page


if __name__ == "__main__":
    search_query = "hvac company"
    google_search = GoogleSearch()
    asyncio.run(google_search.search(search_query))
