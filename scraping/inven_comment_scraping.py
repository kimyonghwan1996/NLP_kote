import requests
from bs4 import BeautifulSoup
import time
import re
import html
import sqlite3

conn = sqlite3.connect("/opt/project/data/identifier.sqlite")
cur = conn.cursor()

def clean_text(text):
    if not text:
        return None

    # HTML 엔티티 변환 (&nbsp; 등)
    text = html.unescape(text)

    # 태그 제거
    text = re.sub(r"<[^>]+>", "", text)

    text = text.replace("\xa0", " ")

    # 공백 정리
    text = re.sub(r"\s+", " ", text)

    return text.strip()


comment_url = "https://www.inven.co.kr/common/board/comment.json.php"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.inven.co.kr/board/mabimo/6259/5702"
}

cur.execute("SELECT url FROM inven_post")
rows = cur.fetchall()

urls = [row[0] for row in rows]

all_comments = []

for url in urls:
    time.sleep(1)

    comeidx = url.split("/")[-2]
    articlecode = url.split("/")[-1]

    data = {
        "comeidx": comeidx,
        "articlecode": articlecode,
        "sortorder": "date",
        "act": "list",
        "out": "json",
        "replyidx": "0"
    }

    response = requests.post(comment_url, headers=headers, data=data)
    response.raise_for_status()
    json_data = response.json()

    comment_blocks = json_data.get("commentlist", [])
    if not comment_blocks:
        continue

    for block in comment_blocks:
        comments = block.get("list", [])
        for c in comments:
            author = c.get("o_name")
            date = c.get("o_date")
            comment = clean_text(c.get("o_comment"))

            all_comments.append({
                "url": url,
                "comeidx": comeidx,
                "articlecode": articlecode,
                "author": author,
                "date": date,
                "comment": comment
            })

            cur.execute("""
                        INSERT INTO inven_comment
                            (articlecode, author, comment, created_at)
                        VALUES (?, ?, ?, ?)
                        """, (
                            articlecode,
                            author,
                            comment.replace("&nbsp",""),
                            date
                        ))
            conn.commit()