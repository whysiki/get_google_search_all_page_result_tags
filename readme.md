# Google Search Scraper

This script utilizes Playwright and BeautifulSoup to perform searches on Google and scrape the results. It is designed to handle dynamic content and can manage resources effectively through asynchronous programming.

## Features

- Perform Google searches and retrieve results.
- Filter out unwanted resources (images and media).
- Retry mechanism for network requests.
- Save HTML content to files, with options to remove CSS and JavaScript.

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

1. **Clone the repository or copy the script:**

   Make sure you have the script saved in a `.py` file.

2. **Run the script:**

   Open a terminal and navigate to the directory where the script is located. You can execute the script with:

   ```bash
   python playwright_google.py
   ```


3. **Specify the search query:**

   In the script, modify the `search_query` variable to your desired search term:

   ```python
   search_query = "your search term"
   ```

4. **View results:**

   The script will create a directory structure under `error` and `testdata`, where it saves the scraped HTML files and any errors encountered during execution. You can navigate to these directories to view the saved files.

## Configuration

- **Proxy Settings:**
  The script has a default proxy set to `http://localhost:62333`. Modify the `self.proxy_url` in the `GoogleSearch` class if you need to change this.

- **Logging:**
  Logs are saved in the `log` directory, named by date. Adjust the logging level and format as needed in the `logger.add()` method.

