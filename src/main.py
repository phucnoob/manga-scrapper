# import sqlite3
#
# conn = sqlite3.connect("data/mangas.sqlite3")
#
# cursor = conn.cursor()
#
# result = cursor.execute("CREATE TABLE IF NOT EXISTS last_updated(time);")
#
# print(result.fetchone())
import asyncio
import json
import logging
import time

import aiohttp

import commons
import info
from list import manga_list
from src import models, upload

logging.basicConfig(level=logging.DEBUG)


async def main():
    async with aiohttp.ClientSession() as session:
        c = 1
        last_update = time.time()
        mangas = manga_list(config, last_update)
        async for manga_url in mangas:

            manga_info, chapters = await info.parse_info(session, manga_url, config, delay=0.2)
            manga_id = models.insert_manga(manga_url)
            db_chapters = models.manga_chapters(manga_id)

            db_id = await upload.upload_manga(session, manga_info)
            if db_id is None:
                continue
            for ch in chapters:
                if ch["src"] not in db_chapters:
                    chapter_images = await info.parse_chapter_images(session, config, ch)
                    chapter_json = dict(name=ch["name"], images=chapter_images)
                    await upload.upload_chapter(session, db_id, chapter_json)

            models.commit()
            c += 1
            if c > 10:
                await commons.cancel_gen(mangas)


with open("data/nettruyen.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
