from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import requests
import asyncio
from fake_useragent import UserAgent
from pathlib import Path

proxy = "http://localhost:62333"
proxies = {"http": proxy, "https": proxy}


async def get_rendered_html(url: str, proxy: str = None) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            proxy={"server": proxy} if proxy else None, headless=False, slow_mo=100
        )
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
    return html


if __name__ == "__main__":
    url = "https://google.com/search?hl=en&q=python"
    normal_html = requests.get(
        url, headers={"User-Agent": UserAgent().random}, proxies=proxies
    ).text
    save_normal_path = Path(__file__).parent / "testdata" / "normal.html"
    save_normal_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_normal_path, "w", encoding="utf-8") as file:
        file.write(normal_html)
    rendered_html = asyncio.run(get_rendered_html(url))
    save_rendered_path = Path(__file__).parent / "testdata" / "rendered.html"
    save_rendered_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_rendered_path, "w", encoding="utf-8") as file:
        file.write(rendered_html)
