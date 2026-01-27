import requests
from bs4 import BeautifulSoup
import time
import sqlite3

conn = sqlite3.connect("../data/identifier.sqlite")
cur = conn.cursor()

base_url = "https://mabinogimobile.nexon.com/News/Notice"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

session = requests.Session()
session.headers.update(headers)

all_posts = []

for page in range(1, 12):  # 1~10페이지
    time.sleep(1)

    params = {
        "headlineId": "0",
        "directionType": "DEFAULT",
        "pageno": str(page),
        "blockStartNo": "0",
        "blockStartKey": "",
        "searchKeywordType": "thread_title",
        "keywords": "점검"
    }

    response = session.get(base_url, params=params)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("ul.list > li.item")
    if not items:
        break

    for item in items:
        thread_id = item.get("data-threadid")
        title = item.select_one("a.title span").get_text(strip=True)
        status =  item.select_one(".type span").get_text(strip=True) if item.select_one(".type span") else None
        regular = "임시" if "임시" in item.select_one("a.title span").get_text(strip=True) else "정기"
        writer = item.select_one(".user_info .name").get_text(strip=True) if item.select_one(".user_info .name") else None
        date = item.select_one("div.date span").get_text(strip=True)

        all_posts.append({
            "thread_id": thread_id,
            "title": title,
            "status": status,
            "writer": writer,
            "regular": regular,
            "date": date
        })

        cur.execute("""
                    INSERT
                    OR IGNORE INTO inspection_post
        (thread_id, title, status, regular, writer, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
                    """, (thread_id, title, status, regular, writer, date))
        conn.commit()
