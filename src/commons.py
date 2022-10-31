# pylint: skip-file

import asyncio
from contextlib import suppress

import aiohttp
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"105\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"105\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8"
}


async def request_get(session: aiohttp.ClientSession, url: str, payload=None, headers=headers, delay=5):
    async with session.get(url, headers=headers, params=payload) as response:
        logger.debug(f"Url: {response.url}")
        logger.debug(f"Response: {response.status}")
        logger.debug(f"Sleep for {delay} seconds.")
        await asyncio.sleep(delay)
        return await response.text()


async def select(soup: BeautifulSoup, selector: str, attr: str = "text"):
    tags = soup.select(selector)
    if tags is None or len(tags) == 0:
        return None

    def func(tag):
        return tag.get_text(strip=True) if attr == "text" else tag.attrs[attr].strip()

    texts = map(func, tags)

    return list(texts)


async def select_one(soup: BeautifulSoup, selector: str, attr: str = "text"):
    result = await select(soup, selector, attr)
    if result is None:
        return ""

    return result[0]


async def download_image(session: aiohttp.ClientSession, url: str, payload=None, headers: dict = headers):
    headers["referer"] = "https://blogtruyen.vn"
    async with session.get(url, headers=headers) as response:
        logger.debug(f"# Download image: {response.status}")
        logger.debug("Sleep 1 second.")
        await asyncio.sleep(1)

        return await response.read()


async def cancel_gen(agen):
    task = asyncio.create_task(agen.__anext__())
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
    await agen.aclose()
