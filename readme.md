# Google Search Scraper

This script utilizes Playwright and BeautifulSoup to perform searches on Google and scrape the results. It is designed to handle dynamic content and manage resources effectively through asynchronous programming.

## Features

- Perform Google searches and retrieve results.
- Filter out unwanted resources (images and media).
- Retry mechanism for network requests.
- Save HTML content to files, with options to remove CSS and JavaScript.
- Support for proxy configuration.

## Requirements

- Python 3.7 or higher
- Dependencies:
  - `httpx`
  - `beautifulsoup4`
  - `rich`
  - `playwright`
  - `loguru`
  - `fake_useragent`

You can install the required packages using pip:

```bash
pip install httpx beautifulsoup4 rich playwright loguru fake-useragent
```

Additionally, make sure to install Playwright browsers:

```bash
playwright install
```

## Usage

1. **Run the script:**

   Open a terminal and navigate to the directory where the script is located. You can execute the script with:

   ```bash
   python playwright_google.py
   ```

   Replace `playwright_google.py` with the actual name of your script file.

2. **Specify the search query:**

   In the script, modify the `search_query` variable to your desired search term:

   ```python
   search_query = "your search term"
   ```

3. **Proxy Configuration:**

   Update the proxy URL by modifying the `update_proxy` method call in the script:

   ```python
   google_search.update_proxy("http://your_proxy_url")
   ```

4. **View results:**

   The script will create a directory structure under `error` and `data`, where it saves the scraped HTML files and any errors encountered during execution. You can navigate to these directories to view the saved files.

## Key Functions

- **`pure_html_remove_css_and_js(html: str) -> str`:** Removes CSS and JavaScript from the given HTML content.
  
- **`save_html(html: str, filename: str, write_mode: str = "w", remove_js_css: bool = False) -> None`:** Saves the HTML content to a specified file. Can optionally remove CSS and JS.

- **`@retry(retry_times: int = 3, delay_range: tuple = (1, 3))`:** Decorator to retry a function call a specified number of times with a delay.

- **`@semaphore_decorator(semaphore: asyncio.Semaphore = asyncio.Semaphore(3))`:** Limits the number of concurrent requests.

- **`async def search(search_query: str, limit_page_range: tuple[int, int] = None) -> None`:** Initiates a search with the specified query.

- **`async def get_pages(self)`:** Retrieves search result pages.

- **`async def get_page(self, context: BrowserContext, url: str) -> int`:** Fetches and processes individual search result pages.
