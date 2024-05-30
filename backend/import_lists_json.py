from sqlmodel import SQLModel, create_engine, Session
import json
from datetime import datetime, timezone

from models import ReadingLists


def main():
    sqlite_file_name = "manga_manager.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    engine = create_engine(sqlite_url, echo=True)

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        with open("MALlists/all_lists.json", 'r') as file:
            data = json.load(file)
            for i in data:
                ts = int(i["created_at"])
                created_at = datetime.fromtimestamp(ts, tz=timezone.utc)
                manga_val = ReadingLists(status=i["status"], score=i["score"], chapters_read=i["num_read_chapters"],
                                         volumes_read=i["num_read_volumes"], added_date=created_at,
                                         manga_title=i["manga_title"],
                                         manga_title_eng=i["manga_english"], chapters_total=i["manga_num_chapters"],
                                         volumes_total=i["manga_num_volumes"],
                                         manga_pub_status=i["manga_publishing_status"],
                                         mal_manga_id=i["manga_id"], manga_url=i["manga_url"],
                                         manga_img_path=i["manga_image_path"])

                session.add(manga_val)
        session.commit()


if __name__ == "__main__":
    main()
