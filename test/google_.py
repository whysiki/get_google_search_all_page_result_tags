from test.some_tools import *


class GoogleSearch:
    def __init__(self) -> None:
        self.base_url = "https://google.com/search"
        self.proxies_dict = dict(
            http="http://localhost:62333", https="http://localhost:62333"
        )
        self.result_tag_set: set = set()
        self.search_url: str = ""
        self.search_query: str = ""

    async def search(self, search_query: str):
        self.search_url = f"{self.base_url}?hl=en&q={search_query}"
        self.search_query = search_query
        await self.get_pages()

    async def get_pages(self):
        async with httpx.AsyncClient(
            proxy=next(iter(self.proxies_dict.values()))
        ) as client:
            # tasks = [self.get_page(client, page) for page in range(10)]
            # await asyncio.gather(*tasks)
            for future in asyncio.as_completed(
                [self.get_page(client, page) for page in range(10)]
            ):
                await future

    async def get_page(self, client: httpx.AsyncClient, page: int):
        url = f"{self.search_url}&start={page * 10}" if page > 0 else self.search_url
        response = await client.get(url)
        console.print(response.url, style="blue")
        response.raise_for_status()
        response_text = response.text
        soup = BeautifulSoup(response_text, "html.parser")
        searched_result_tag_set = soup.select("#rso > div.MjjYud")
        if searched_result_tag_set:
            old_result_tag_set_len = len(self.result_tag_set)
            for tag in searched_result_tag_set:
                self.result_tag_set.add(tag)
                file_path = Path(
                    f"testdata/search_{self.search_query}_page_{page}.html"
                )
                write_mode = "w" if not file_path.exists() else "a"
                save_html(tag.prettify(), file_path, write_mode=write_mode)
            new_result_tag_set_len = len(self.result_tag_set)
            console.print(
                f"Added {new_result_tag_set_len - old_result_tag_set_len} results",
                style="green",
            )
        else:
            save_html(
                response.text,
                f"testdata/error_response_{self.search_query}_page_{page}.html",
            )
            console.print("No results found", style="red")


if __name__ == "__main__":
    search_query = "python"
    google_search = GoogleSearch()
    asyncio.run(google_search.search(search_query))


# #rso
html_text = page.content()
soup = BeautifulSoup(html_text, "html.parser")
# >>> searched_result_tag_set = soup.select("#rso > div")

soup.select("#rso > div").prettify()

pure_html_remove_css_and_js(soup.find("#rso > div").prettify())
# next_tag_selector = "tbody > tr > td.NKTSme"
next_page_seletor = "#pnnext"
