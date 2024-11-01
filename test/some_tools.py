import asyncio
import httpx
from bs4 import BeautifulSoup
from pathlib import Path
from rich.console import Console
from typing import List
import re
from functools import wraps, lru_cache

console = Console()


def pure_html_remove_css_and_js(html: str) -> str:
    return re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.DOTALL)


def save_html(html: str, filename: str | Path, write_mode: str = "w") -> None:
    assert isinstance(filename, (str, Path)), "Filename must be a string or Path object"
    save_path = Path(filename) if isinstance(filename, str) else filename
    assert save_path.suffix == ".html", "Filename must have .html extension"
    if not save_path.parent.exists():
        save_path.parent.mkdir(parents=True, exist_ok=True)
        console.print(f"Creating directory {save_path.parent}", style="blue")
    with open(filename, write_mode, encoding="utf-8") as file:
        file.write(html)


d = dict(http="http://localhost:62333", https="http://localhost:62333")

print(iter(d.values()))
print(next(iter(d.values())))
