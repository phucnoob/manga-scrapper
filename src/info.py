
import asyncio
import json

from pathlib import Path
from aiofile import async_open
import aiohttp
from bs4 import BeautifulSoup
from .commons import download_image, make_request, select


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
                print(manga)
                print(f"Manga[{manga['name']}]")
                manga_path = await save_info(manga)
                chapters = await parse_chapters(html)
                for chapter in chapters:
                    print(chapter["name"])
                    await save_chapter(session, manga_path, chapter)


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
    info_path = manga_dir/"info.json"

    with open(info_path, "w", encoding="utf-8") as info_file:
        json.dump(manga, info_file, ensure_ascii=False, indent=4)

    return manga_dir


async def parse_chapter_images(session: aiohttp.ClientSession, chapter: dict):
    url = chapter["src"]
    html = await make_request(session, url)
    soup = BeautifulSoup(html, "lxml")

    images = soup.select("#content > img")

    return list(map(lambda tag: tag.attrs["src"], images))

# pylint: disable=line-too-long


async def parse_info(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        manga = manga_template.copy()
        manga["name"] = (await select(soup, "#breadcrumbs>span:nth-child(2)")).split(">")[-1].strip()

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
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
