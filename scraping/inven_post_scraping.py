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


inven_url = "https://www.inven.co.kr/search/mabimo/article/%EC%A0%90%EA%B2%80/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

session = requests.Session()
session.headers.update(headers)

inven_posts = []

for page in range(1, 17):  # 1~10페이지
    time.sleep(1)

    response = session.get(f"{inven_url}{page}")
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select(
        "#mabimoBody > div.commu-wrap > section > article > section.commu-center > div.commu-body.pcMain > div > "
        "div.isearch_sub_wrap > div.section_box.noboard > div.section_body > ul > li")
    if not items:
        break

    for item in items:
        time.sleep(0.5)
        url = item.select_one("h1 > a").get('href')

        article_res = session.get(url)
        article_soup = BeautifulSoup(article_res.text, "html.parser")
        article_tag = article_soup.select_one("#tbArticle > div.articleMain")
        article = article_tag.get_text(strip=True) if article_tag else None

        comeidx = url.split("/")[-2]
        articlecode = url.split("/")[-1]
        title = item.select_one("h1 > a").get_text(strip=True)
        article = clean_text(article)
        date = item.select_one("div > p").get_text(strip=True)

        inven_posts.append({
            "articlecode": articlecode,
            "comeidx": comeidx,
            "url": url,
            "title": title,
            "article": article,
            "date": date
        })

        cur.execute("""
                    INSERT INTO inven_post
                        (articlecode, comeidx, url, title, article, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        articlecode,
                        comeidx,
                        url,
                        title,
                        article,
                        date
                    ))
        conn.commit()
