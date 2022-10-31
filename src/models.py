import sqlite3
from typing import Any

DDL_TABLES = """
CREATE TABLE IF NOT EXISTS last_updated(
    time INTEGER DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS mangas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chapters (
    manga_id INTEGER NOT NULL,
    url TEXT,
    FOREIGN KEY (manga_id) REFERENCES mangas(id)
);
"""

conn = sqlite3.connect("data/mangas.sqlite3")
conn.executescript(DDL_TABLES)
cur = conn.cursor()


def last_updated() -> int:
    (result,) = cur.execute("SELECT time FROM last_updated;").fetchone()
    return result


def manga_exists_in_database(url: str) -> bool:
    (result,) = cur.execute("SELECT COUNT(1) FROM mangas WHERE url = ?", (url,)).fetchone()
    return result == 1


def find_manga_from_url(url: str) -> int | None:
    cur.row_factory = lambda cursor, row: row[0]
    result_set = cur.execute("SELECT id, url FROM mangas WHERE url = ?", (url,)).fetchone()
    cur.row_factory = None

    return result_set


def manga_chapters(manga_id: int) -> list:
    cur.row_factory = lambda cursor, row: row[0]
    result = cur.execute("SELECT url FROM chapters WHERE manga_id = ?", (manga_id,)).fetchall()
    cur.row_factory = None
    return result


def insert_chapters(manga_id, chapters: list):
    records = []
    for ch in chapters:
        records.append((manga_id, ch))
    cur.executemany("INSERT INTO chapters(manga_id, url) VALUES (?, ?)", records)


def insert_manga(url: str) -> int | None:
    manga_id = find_manga_from_url(url)
    if manga_id is None:
        cur.execute("INSERT INTO mangas(url) VALUES (?)", (url,))
        conn.commit()
        return cur.lastrowid
    else:
        return manga_id


def commit():
    conn.commit()

# print(last_updated())
# Kiem tra xem
