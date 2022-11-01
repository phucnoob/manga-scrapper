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
import sys

import aiohttp

import commons
import info
from src import list
from src import models, upload

logging.basicConfig(level=logging.DEBUG)


async def main(_config: dict):
    async with aiohttp.ClientSession() as session:

        synced = False if len(sys.argv) <= 1 else True

        if not synced:
            models.clear() # destroy any data whhen not in synced mode
        mangas = list.manga_list(_config) if synced else list.manga_list_reverse(config)
        async for manga_url in mangas:
            try:
                manga_info, chapters = await info.parse_info(session, manga_url, _config, delay=0.2)
                manga_id = models.insert_manga(manga_url)
                db_chapters = models.manga_chapters(manga_id)

                db_id = await upload.upload_manga(session, manga_info)
                if db_id is None:
                    continue

                continue_sync = False
                new_chapters = []
                for ch in chapters:
                    if ch["src"] not in db_chapters:
                        continue_sync = True
                        chapter_images = await info.parse_chapter_images(session, _config, ch)
                        chapter_json = dict(name=ch["name"], images=chapter_images)
                        new_chapters.append(ch["src"])
                        await upload.upload_chapter(session, db_id, chapter_json)

                # IF there is no new chapter in 1 manga then no need to sync more
                if not continue_sync:
                    await commons.cancel_gen(mangas)

                models.insert_chapters(db_id, new_chapters)
                models.commit()

            except Exception as e:
                logging.debug(e)


with open("data/nettruyen.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(config))
