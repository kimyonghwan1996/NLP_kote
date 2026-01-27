import requests
from bs4 import BeautifulSoup
import time
import re
import html
import sqlite3
from urllib.parse import urlparse, parse_qs

conn = sqlite3.connect("/opt/project/data/identifier.sqlite")
cur = conn.cursor()

def clean_text(text):
    if not text:
        return None

    # HTML 엔티티 변환 (&nbsp; 등)
    # text = html.unescape(text)

    # 태그 제거
    text = re.sub(r"<[^>]+>", "", text)

    text = text.replace("\xa0", " ")

    # 공백 정리
    text = re.sub(r"\s+", " ", text)

    return text.strip()

comment_url = 'https://gall.dcinside.com/board/comment/'

cur.execute("SELECT url FROM dc_post")
rows = cur.fetchall()

urls = [row[0] for row in rows]

all_comments = []

for url in urls:
    time.sleep(1)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": url
    })

    html = session.get(url).text

    patterns = [
        r'e_s_n_o["\']?\s*[:=]\s*["\']([a-zA-Z0-9]+)["\']',
        r'data-esno=["\']([a-zA-Z0-9]+)["\']'
    ]
    print(html)
    e_s_n_o = None
    for p in patterns:
        m = re.search(p, html)
        if m:
            e_s_n_o = m.group(1)
            break

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    gallery_id = qs["id"][0]
    article_no = qs["no"][0]

    data = {
        "id": 'mabinogimobile',
        "no": article_no,
        "cmt_id": 'mabinogimobile',
        "cmt_no": article_no,
        "e_s_n_o": '3eabc219ebdd65fe3eef86ec', #셀레니움으로 가져오기로 바꿀 것
        "comment_page": 1,
        "sort": "D",
        "_GALLTYPE_": "M"
    }

    response = session.post(comment_url, data=data)

    data = response.json()
    comments = data.get("comments", [])
    if not comments:
        continue

    for c in comments:
        author = c.get("name")
        date = c.get("reg_date")
        comment = clean_text(c.get("memo"))

        all_comments.append({
            "url": url,
            "articlecode": article_no,
            "author": author,
            "date": date,
            "comment": comment
        })

    cur.execute("""
                INSERT INTO dc_comment
                    (articlecode, author, comment, created_at)
                VALUES (?, ?, ?, ?)
                """, (
                    article_no,
                    author,
                    comment,
                    date
                ))
    conn.commit()