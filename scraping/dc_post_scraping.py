import requests
from bs4 import BeautifulSoup
import time
import re
import html
import sqlite3

conn = sqlite3.connect("../data/identifier.sqlite")
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


dc_url = "https://gall.dcinside.com/mgallery/board/view/?id=mabinogimobile&no=2163873&s_type=search_subject_memo&s_keyword=%EC%A0%90%EA%B2%80&page="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

session = requests.Session()
session.headers.update(headers)

dc_posts = []

for page in range(1, 5):  # 1~10페이지
    time.sleep(1)

    response = session.get(f"{dc_url}{page}")
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select(
        "#bottom_listwrap > section.left_content.result > article > div.gall_listwrap.list > table > tbody > tr")
    if not items:
        break
    for item in items:
        time.sleep(0.5)
        url = "https://gall.dcinside.com/mgallery/board/view/?id=mabinogimobile&no="

        articlecode = item.select_one("td.gall_num").get_text(strip=True)
        if articlecode not in ('-','AD') and articlecode is not None:
            title = item.select_one("td.gall_tit.ub-word").get_text(strip=True)
            date = item.select_one("td.gall_date").get_text(strip=True)

            article_res = session.get(f"{url}{articlecode}")
            article_soup = BeautifulSoup(article_res.text, "html.parser")
            article_tag = article_soup.select_one("#container > section > article:nth-child(3) > div.view_content_wrap > div > div.inner.clear > div.writing_view_box")
            article = article_tag.get_text(strip=True) if article_tag else None
            article = clean_text(article)

            dc_posts.append({
                "articlecode": articlecode,
                "url": f"{url}{articlecode}",
                "title": title,
                "article": article,
                "date": date
            })

            cur.execute("""
                        INSERT INTO dc_post
                            (articlecode, url, title, article, created_at)
                        VALUES (?, ?, ?, ?, ?)
                        """, (
                            articlecode,
                            f"{url}{articlecode}",
                            title,
                            article,
                            date
                        ))
            conn.commit()
