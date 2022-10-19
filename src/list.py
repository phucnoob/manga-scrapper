"""Parse the website and print all manga link
"""
import asyncio
import json
from enum import IntEnum
from urllib import parse

import aiohttp
from bs4 import BeautifulSoup

import commons


manga_url_pool = set()


async def get_last_page(session: aiohttp.ClientSession, url):
    html = await commons.request_get(session, url, delay=1)
    soup = BeautifulSoup(html, "lxml")

    link = await commons.select_one(soup, ".pagination > li:last-child a", "href")
    page = parse.parse_qs(parse.urlparse(link).query)["page"][0]

    return int(page)


async def get_manga_list(html, config):
    soup = BeautifulSoup(html, "lxml")
    links = await commons.select(soup, config["selector"]["link_from_search"], "href")

    return links


class OrderBy(IntEnum):
    NAME = 1
    CHAPTERS = 2
    VIEWS = 3
    COMMENT = 4
    TIME = 5


async def main(config: dict):

    with open("data/mangas.txt", "r", encoding='utf-8') as init_data:
        for line in init_data:
            manga_url_pool.add(line)

    async with aiohttp.ClientSession() as session:

        url = config["search"]
        last_page = await get_last_page(session, url)
        payload = {
            "page": 1
        }
        for page in range(1, last_page + 1):
            payload["page"] = page
            await parse_data(session, url, payload, config)

    with open("mangas.txt", "w", encoding='utf-8') as out_data:
        for url in manga_url_pool:
            out_data.write(f"{url}\n")


async def parse_data(session, url, payload, config):
    html = await commons.request_get(session, url, payload, delay=0.2)
    manga_links = await get_manga_list(html, config)
    print(json.dumps(manga_links, indent=4))
    manga_url_pool.update(manga_links)


def start():
    with open("data/nettruyen.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main(config))


if __name__ == '__main__':
    start()
