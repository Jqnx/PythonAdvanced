import requests
import click
from requests.models import Response
from bs4 import BeautifulSoup
import re

@click.command()
@click.argument('url')
def main(url: str) -> None:
    res = fetch(url)
    words = get_words(res.text)
    print(words)

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

def get_words(input: str) -> list[str]:
   html = BeautifulSoup(input, "html.parser")
   return re.findall(r"\b\w+\b", html.get_text(","))
