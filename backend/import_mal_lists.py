import sqlite3
import json
from datetime import datetime, timezone

conn = sqlite3.connect("manga_manager.db")
cur = conn.cursor()

with open("MALlists/all_lists.json", 'r') as file:
    data = json.load(file)
    for i in data:
        ts = int(i["created_at"])
        created_at = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        print(created_at)
        cur.execute("INSERT INTO readinglists (status, score, chapters_read, volumes_read, manga_title, "
                    "manga_title_eng, chapters_total, volumes_total, manga_pub_status, mal_manga_id, manga_url, "
                    "manga_img_path, added_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (i["status"], i["score"], i["num_read_chapters"], i["num_read_volumes"],
                     i["manga_title"], i["manga_english"], i["manga_num_chapters"],
                     i["manga_num_volumes"],
                     i["manga_publishing_status"],
                     i["manga_id"], i["manga_url"],
                     i["manga_image_path"], created_at))
    conn.commit()
    conn.close()
