# pylint: skip-file

import asyncio
import aiohttp
from bs4 import BeautifulSoup


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


async def make_request(session: aiohttp.ClientSession, url: str, payload=None, headers=headers, delay=5):
    async with session.get(url, headers=headers, params=payload) as response:
        print(f"Response: {response.status}")
        print(f"Sleep for {delay} seconds.")
        await asyncio.sleep(delay)
        return await response.text()


async def select(soup: BeautifulSoup, selector: str, attr: str = "text"):
    tag = soup.select_one(selector)
    if tag is None:
        return None
    else:
        return tag.attrs[attr].strip() if attr != "text" else tag.text.strip()


async def download_image(session: aiohttp.ClientSession, url: str, payload=None, headers: dict = headers):

    headers["referer"] = "https://blogtruyen.vn"
    async with session.get(url, headers=headers) as response:
        print(f"# Download image: {response.status}")
        print("Sleep 1 second.")
        await asyncio.sleep(1)

        return await response.read()
