"""Parse the website and print all manga link
"""
import asyncio
from enum import IntEnum

import aiohttp
from bs4 import BeautifulSoup

import commons

DOMAIN_NAME = "https://blogtruyen.vn"
MAX_PAGES = 1179
CURRENT_MANGAS = 23567

manga_url_pool = set()


async def fetch_mangas_count(session: aiohttp.ClientSession, url="https://blogtruyen.vn/danhsach/tatca"):
    html = await commons.make_request(session, url, delay=1)
    soup = BeautifulSoup(html, "lxml")

    text = await commons.select(
        soup, "#wrapper > section.main-content > div > div.col-md-8 > div > section > div.head.uppercase")

    return int(text.split()[1])


async def get_manga_list(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        main_div = soup.select_one(".list")
        for item in main_div.select("p>span>a"):
            manga_url_pool.add(item.attrs['href'])
            url = f"{DOMAIN_NAME}{item.attrs['href']}"
            print(url)
            # print(url)
    except Exception:  # pylint: disable=broad-except
        return False

    return True


class OrderBy(IntEnum):
    NAME = 1
    CHAPTERS = 2
    VIEWS = 3
    COMMENT = 4
    TIME = 5


async def main():

    with open("mangas.txt", "r", encoding='utf-8') as init_data:
        for line in init_data:
            manga_url_pool.add(line)

    async with aiohttp.ClientSession() as session:
        manga_count = await fetch_mangas_count(session)
        if manga_count < len(manga_url_pool):
            return

        url = "https://blogtruyen.vn/ajax/Search/AjaxLoadListManga"
        payload = {
            "key": "tatca",
            "orderBy": OrderBy.TIME,
            "p": 1
        }
        page = 1
        should_continue = True
        while should_continue:
            payload["p"] = page
            page += 1
            should_continue = await parse_data(session, url, payload)

    with open("mangas.txt", "w", encoding='utf-8') as out_data:
        for url in manga_url_pool:
            out_data.write(f"{url}\n")


async def parse_data(session, url, payload):
    html = await commons.make_request(session, url, payload, delay=1)
    return await get_manga_list(html)


def start():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
