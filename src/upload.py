import logging

import aiohttp

URL = "http://localhost:8080/api/v1/manga/add"
CHAPTER_URL = "http://localhost:8080/api/v1/chapter/add"

logger = logging.getLogger(__name__)


async def upload_manga(session: aiohttp.ClientSession, manga_info: dict):
    response = await session.post(URL, json=manga_info)

    json_data = await response.json()

    if json_data["success"]:
        return int(json_data["data"])
    else:
        return None


async def upload_chapter(session: aiohttp.ClientSession, manga_id: int, chapter: dict):
    params = {
        "manga_id": manga_id
    }
    response = await session.post(CHAPTER_URL, params=params, json=chapter)
    logger.debug(f"Url: {response.url}")
    logger.debug(f"Response: {await response.json()}")
