from collections import Counter
from urllib.parse import urlparse, urljoin

import requests
import click
from requests.models import Response
from bs4 import BeautifulSoup
import re
from spellchecker import SpellChecker


@click.command()
@click.argument('url')
def main(url: str):
    searched = []
    count = Counter()
    words = search(url, count, searched)
    print(words)

def search(url: str, counter: Counter, searched: list[str], depth=0):
    print(depth)
    if depth > 1:
        return counter
    if url not in searched:
        depth += 1
        res = fetch(url)
        searched.append(url)
        try:
            words = get_words(res.text)
            counter.update(words)
        except AttributeError:
            return
        links = get_links(res.text, url)
        for link in links:
            search(link, counter, searched, depth)
        return counter


def fetch(url: str) -> Response | None:
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res
    except requests.exceptions.HTTPError as e:
        print(f"Request failed with status code: {res.status_code}")
        return
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return

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
