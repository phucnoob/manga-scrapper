
import asyncio
import json
import sys

from pathlib import Path
import aiohttp
from attr import attr
from bs4 import BeautifulSoup, Tag
from .commons import make_request


DOMAIN_NAME = "https://blogtruyen.vn"
manga_template = {
    "author": "",
    "cover": "",
    "description": "",
    "name": "",
    "otherName": "",
    "status": "",
    "genres": None
}

chapter_info_template = {
    "name": "",
    "src": ""
}


async def main(sync=False):
    async with aiohttp.ClientSession() as session:
        with open("mangas.txt", encoding="utf-8") as urls_file:
            for (index, url) in enumerate(urls_file):
                html = await make_request(session, url, None)
                manga = await parse_info(html)
                chapters = await parse_chapters(html)
                # await save_info(manga)
                print(json.dumps(chapters, indent=4))
                print(f"Saved #{index}")


async def save_info(manga):
    manga_dir = Path(f"data/{manga['name']}")
    manga_dir.mkdir(parents=True, exist_ok=True)
    info_path = manga_dir/"info.json"

    with open(info_path, "w", encoding="utf-8") as info_file:
        json.dump(manga, info_file, ensure_ascii=False, indent=4)


async def select(soup: BeautifulSoup, selector: str, attr: str = "text"):
    tag = soup.select_one(selector)
    if tag is None:
        return None
    elif not tag.has_attr(attr):
        return None
    else:
        return tag.attrs[attr].strip() if attr != "text" else tag.get_text(strip=True)

# pylint: disable=line-too-long


async def parse_info(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        manga = manga_template.copy()
        manga["name"] = await select(soup, "#breadcrumbs > span:nth-child(2)")

        manga["otherName"] = await select(soup, "#wrapper > section.main-content > div > div.col-md-8 > section > div.description > p:nth-child(1) > span")

        manga["genres"] = list(map(lambda tag: tag.text.strip() if tag is not None else "", soup.select(
            ".description>p>span.category>a")))

        manga["status"] = await select(
            soup, "#wrapper > section.main-content > div > div.col-md-8 > section > div.description > p:nth-child(5) > span")

        manga["description"] = await select(
            soup, "#wrapper > section.main-content > div > div.col-md-8 > section > div.detail > div.content > p")

        manga["author"] = await select(
            soup, "#wrapper > section.main-content > div > div.col-md-8 > section > div.description > p:nth-child(2) > a")

        manga["cover"] = await select(
            soup, "#wrapper > section.main-content > div > div.col-md-8 > section > div.thumbnail > img", "src")

    except AttributeError as error:
        print(error)

    return manga


async def parse_chapters(html: str):
    soup = BeautifulSoup(html, "lxml")
    tags = soup.select("#loadChapter span.title > a")
    chapters = []
    for tag in tags:
        chapter = chapter_info_template.copy()
        chapter["name"] = tag.get_text(strip=True)
        chapter["src"] = f"{DOMAIN_NAME}{tag.attrs['href']}"
        chapters.append(chapter)

    return chapters


def start():

    # sync = True if sys.argv[1] == "sync" else False

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
