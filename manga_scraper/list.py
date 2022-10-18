"""Parse the website and print all manga link
"""
import asyncio
from enum import IntEnum

import aiohttp
from bs4 import BeautifulSoup
from . import commons


DOMAIN_NAME = "https://blogtruyen.vn"
MAX_PAGES = 1179


async def get_manga_list(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        main_div = soup.select_one(".list")
        for item in main_div.select("p>span>a"):
            url = f"{DOMAIN_NAME}{item.attrs['href']}"
            print(url)
            # print(url)
    except Exception:  # pylint: disable=broad-except
        print("Error.")


class OrderBy(IntEnum):
    NAME = 1
    CHAPTERS = 2
    VIEWS = 3
    COMMENT = 4
    TIME = 5


async def main():
    async with aiohttp.ClientSession() as session:
        url = "https://blogtruyen.vn/ajax/Search/AjaxLoadListManga"
        payload = {
            "key": "tatca",
            "orderBy": OrderBy.VIEWS,
            "p": 1
        }
        for page in range(1, MAX_PAGES + 1):
            payload["p"] = page
            await parse_data(session, url, payload)


async def parse_data(session, url, payload):
    html = await commons.make_request(session, url, payload)
    await get_manga_list(html)


def start():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
