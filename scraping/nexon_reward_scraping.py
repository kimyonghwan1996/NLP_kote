import requests
from bs4 import BeautifulSoup
import time
import re
import sqlite3

conn = sqlite3.connect("../data/identifier.sqlite")
cur = conn.cursor()

base_url = "https://mabinogimobile.nexon.com/News/Notice"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

session = requests.Session()
session.headers.update(headers)

cur.execute("SELECT thread_id FROM inspection_post")
rows = cur.fetchall()

thread_ids = [row[0] for row in rows]

reward_list = []

for thread_id in thread_ids:  # 1~10페이지
    time.sleep(1)

    response = session.get(f"{base_url}/{thread_id}")
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.select_one("table.Table")
    if not table:
        continue

    rows = table.select("tr")[1:]

    for row in rows:
        cols = row.select("td")
        if len(cols) < 2:
            continue

        item_name = cols[0].get_text(strip=True)
        quantity_text = cols[1].get_text(strip=True)
        quantity = re.sub(r"[^\d]", "", quantity_text)
        quantity = int(quantity) if quantity else None

        reward_list.append({
            "thread_id": thread_id,
            "item_name": item_name,
            "quantity": quantity,
            "raw_quantity": quantity_text
        })

        cur.execute("""
                    INSERT INTO inspection_reward
                        (thread_id, item_name, quantity)
                    VALUES (?, ?, ?)
                    """, (thread_id, item_name, quantity))
        conn.commit()
