import asyncio
import re
from collections import Counter
from urllib.parse import urljoin, urlparse

import aiohttp
import click
import requests
from bs4 import BeautifulSoup
from spellchecker import SpellChecker


@click.command()
@click.argument("url")
@click.option("-d", "--depth", default=2, help="max depth of pages to search")
@click.option(
    "--async",
    "sync",
    flag_value=True,
    default=False,
    help="run the scraper in async mode",
)
def main(url: str, depth: int, sync: bool):
    searched = []
    count = Counter()
    if sync:
        try:
            res = asyncio.run(run_async(url, depth, searched, count))
            print(res)
        except NotImplementedError as e:
            print(e)
    else:
        res = run_sync(url, depth, searched, count)
        print(res)


def run_sync(url: str, depth: int, searched: list, count: Counter):
    words = search(url, count, searched, depth)
    return words


async def run_async(url: str, depth: int, searched: list, count: Counter):
    words = await async_search(url, count, searched, depth)
    return words


def search(url: str, counter: Counter, searched: list[str], max_depth, current_depth=1):
    if current_depth > max_depth:
        return counter
    if url not in searched:
        current_depth += 1
        text = fetch(url)
        searched.append(url)
        if not text:
            return
        try:
            words = get_words(text)
            counter.update(words)
        except AttributeError:
            return
        links = get_links(text, url)
        for link in links:
            search(link, counter, searched, max_depth, current_depth)
        return counter


async def async_search(
    url: str, counter: Counter, searched: list[str], max_depth, current_depth=1
):
    if current_depth > max_depth:
        return counter
    if url not in searched:
        current_depth += 1
        text = await async_fetch(url)
        searched.append(url)
        if not text:
            return
        try:
            words = get_words(text)
            counter.update(words)
        except AttributeError:
            return
        links = get_links(text, url)
        tasks = [
            async_search(link, counter, searched, max_depth, current_depth)
            for link in links
        ]
        await asyncio.gather(*tasks)
        return counter


def fetch(url: str) -> str:
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.text
    except requests.exceptions.HTTPError:
        print(f"Request failed with status code: {res.status_code}")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return ""


async def async_fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as res:
                res.raise_for_status()
                return await res.text()
        except aiohttp.ClientResponseError:
            print(f"Request failed with status code: {res.status}")
            return ""
        except aiohttp.ClientConnectionError as e:
            print(f"Connection error: {e}")
            return ""


def get_words(input: str) -> set[str]:
    spell = SpellChecker()
    html = BeautifulSoup(input, "html.parser")
    split = re.findall(r"\b\w+\b", html.get_text(","))
    return spell.known(split)


def get_links(input: str, url: str) -> list[str]:
    html = BeautifulSoup(markup=input, features="html.parser")
    a = html.find_all("a")

    links = []
    for item in a:
        link = str(item.get("href"))
        parsed = urlparse(url=link, scheme="http")
        if link and not parsed.netloc:
            link = urljoin(url, parsed.path)
        links.append(link)
    return links
