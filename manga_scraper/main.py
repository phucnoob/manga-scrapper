import asyncio
from enum import Enum, IntEnum

import aiohttp
from bs4 import BeautifulSoup
from . import config


DOMAIN_NAME = "https://blogtruyen.vn"
parsed_urls = 0


async def make_request(session: aiohttp.ClientSession, url: str, payload: dict):
    async with session.get(url, headers=config.headers, params=payload) as response:
        return await response.text()


def get_manga_list(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        main_div = soup.select_one(".list")
        for item in main_div.select("p>span>a"):
            url = f"{DOMAIN_NAME}{item.attrs['href']}"
            print(url)
            # print(url)
    except Exception:
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
        for page in range(1, 1780):
            payload["p"] = page
            await parse_data(session, url, payload)


async def parse_data(session, url, payload):
    html = await make_request(session, url, payload)
    get_manga_list(html)


def start():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
