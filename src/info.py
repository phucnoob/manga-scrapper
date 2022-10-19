import asyncio
import json
import sys

from pathlib import Path
from urllib.parse import urlparse

from aiofile import async_open
import aiohttp
from bs4 import BeautifulSoup
from commons import download_image, request_get, select, select_one

DOMAIN_NAME = ""
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


async def main(config: dict = None):
    async with aiohttp.ClientSession() as session:
        with open("data/mangas.txt", encoding="utf-8") as urls_file:
            for (index, path) in enumerate(urls_file):
                url = path
                html = await request_get(session, url, delay=1)
                manga = await parse_info(html, config)
                data = json.dumps(manga, ensure_ascii=False, indent=4)

                print(data)
                local_host = "http://localhost:8080/api/v1/manga/add"
                response = await session.post(local_host, json=manga)
                print(f"Server#\n {await response.json()}")

                if index > 100:
                    break
                # print(manga)
                # print(f"Manga[{manga['name']}]")
                # manga_path = await save_info(manga)
                # chapters = await parse_chapters(html)
                # for chapter in chapters:
                #     print(chapter["name"])
                #     await save_chapter(session, manga_path, chapter)


async def save_chapter(session, manga_path, chapter):
    image_links = await parse_chapter_images(session, chapter)
    chapter_path: Path = manga_path / chapter["name"]
    chapter_path.mkdir(parents=True, exist_ok=True)
    jobs = []
    for index, image_link in enumerate(image_links):
        image_path = chapter_path / f"image_{index}.jpg"
        jobs.append(save_image(session, image_link, image_path))

    await asyncio.gather(*jobs)


async def save_image(session, image_link, image_path):
    image_data = await download_image(session, image_link)
    async with async_open(image_path, "wb") as image:
        await image.write(image_data)


async def save_info(manga):
    manga_dir = Path(f"data/{manga['name']}")
    manga_dir.mkdir(parents=True, exist_ok=True)
    info_path = manga_dir / "info.json"

    with open(info_path, "w", encoding="utf-8") as info_file:
        json.dump(manga, info_file, ensure_ascii=False, indent=4)

    return manga_dir


async def parse_chapter_images(session: aiohttp.ClientSession, chapter: dict):
    url = chapter["src"]
    html = await request_get(session, url)
    soup = BeautifulSoup(html, "lxml")

    images = soup.select("#content > img")

    return list(map(lambda tag: tag.attrs["src"], images))


# pylint: disable=line-too-long


async def parse_info(html, config: dict):
    try:
        soup = BeautifulSoup(html, "lxml")
        selector = config["selector"]
        manga = manga_template.copy()
        manga["name"] = await select_one(soup, selector["name"])

        manga["otherName"] = await select_one(soup, selector["otherName"])

        manga["genres"] = await select(soup, selector["genres"])

        manga["status"] = await select_one(soup, selector["status"])

        manga["description"] = await select_one(soup, selector["description"])

        manga["author"] = await select_one(soup, selector["author"])

        manga["cover"] = await select_one(soup, selector["cover"], "src")

        protocol = urlparse(config['url']).scheme
        manga["cover"] = f"{protocol}:{manga['cover']}"

        return manga
    except AttributeError as error:
        print(error)

    return None


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
    if len(sys.argv) <= 1:
        raise ValueError("Error, please specify config path")
    path = Path(sys.argv[1])

    if not path.exists():
        raise ValueError(f"Config file {path.absolute()} not exists.")

    with open(path, "r", encoding="utf-8") as json_str:

        config = json.load(json_str)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main(config))


if __name__ == '__main__':
    start()
