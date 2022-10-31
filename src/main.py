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


logging.basicConfig(level=logging.DEBUG)


async def main():
    async with aiohttp.ClientSession() as session:
        c = 1
        last_update = time.time()
        mangas = manga_list(config, last_update)
        async for manga_url in mangas:
            manga_info = await info.parse_info(session, manga_url, config, delay=0.2)
            local_host = "http://localhost:8080/api/v1/manga/add"
            response = await session.post(local_host, json=manga_info)
            logging.debug(f"Server#\n {await response.json()}")

            c += 1
            if c > 100:
                await commons.cancel_gen(mangas)


with open("data/nettruyen.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
