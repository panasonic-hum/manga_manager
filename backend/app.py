from fastapi import FastAPI, Query, HTTPException
import models
from sqlmodel import Session, select
from typing import Annotated
from logging.config import dictConfig
import logging
from app_logger import LogConfig
from datetime import datetime, timezone

dictConfig(LogConfig().dict())
logger = logging.getLogger("manga_manager")

app = FastAPI()


@app.on_event("startup")
def startup():
    models.create_db_and_tables()


@app.get("/mangamanager/lists/all")
def all_mangalists():
    with Session(models.engine) as session:
        all_lists = session.exec(select(models.ReadingLists)).all()
        return all_lists


@app.get("/mangamanager/lists/reading")
def reading_mangalist():
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 1)
        currread_list = session.exec(statement)
        return currread_list.all()


@app.get("/mangamanager/lists/read")
def read_mangalist():
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 2)
        read_list = session.exec(statement)
        return read_list.all()


@app.get("/mangamanager/lists/onhold")
def onhold_mangalist():
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 3)
        onhold_list = session.exec(statement)
        return onhold_list.all()


@app.get("/mangamanager/lists/dropped")
def dropped_mangalist():
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 4)
        dropped_list = session.exec(statement)
        return dropped_list.all()


@app.get("/mangamanager/lists/plantoread")
def ptr_mangalist():
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 6)
        ptr_list = session.exec(statement)
        return ptr_list.all()


@app.get("/mangamanager/manga_info/mark_total")
def get_mark_total(mark_type: models.MarkType, manga_title_eng: Annotated[str,
Query(description="manga title is case sensitive")]):
    with Session(models.engine) as session:
        if mark_type is models.MarkType.chapter:
            chapter_total = session.exec(
                select(models.ReadingLists.chapters_total)
                .where(models.ReadingLists.manga_title_eng == manga_title_eng)
            ).one_or_none()
            return chapter_total
        elif mark_type is models.MarkType.volume:
            volume_total = session.exec(
                select(models.ReadingLists.volumes_total)
                .where(models.ReadingLists.manga_title_eng == manga_title_eng)
            ).one_or_none()
            return volume_total
        else:
            return "mark type didn't match"


@app.get("/mangamanager/manga_info/read_total")
def get_read_total(mark_type: models.MarkType, manga_title_eng: Annotated[str,
Query(description="manga title is case sensitive")]):
    with Session(models.engine) as session:
        if mark_type is models.MarkType.chapter:
            chapter_total = session.exec(
                select(models.ReadingLists.chapters_read)
                .where(models.ReadingLists.manga_title_eng == manga_title_eng)
            ).one_or_none()
            return chapter_total
        elif mark_type is models.MarkType.volume:
            volume_total = session.exec(
                select(models.ReadingLists.volumes_read)
                .where(models.ReadingLists.manga_title_eng == manga_title_eng)
            ).one_or_none()
            return volume_total
        else:
            return "mark type didn't match"


@app.get("/mangamanager/manga_info/get_series", response_model=models.AllMangaInfo)
def get_all_manga_info(manga_title_eng: str):
    with Session(models.engine) as session:
        manga = session.query(models.ReadingLists).filter(
            models.ReadingLists.manga_title_eng.ilike(f"%{manga_title_eng}%"))
        return manga.first()


@app.get("/mangamanager/manga_info/get_id", response_model=models.MangaInfoId)
def get_manga_id(manga_title_eng: str):
    with Session(models.engine) as session:
        manga = session.query(models.ReadingLists).filter(models.ReadingLists.manga_title_eng.ilike(manga_title_eng))
        return manga.first()


@app.patch("/mangamanager/update/update_read_status", response_model=models.ReadUpdate)
def update_mark_status(mark_type: models.MarkType, manga_title_eng: str, update_type: models.UpdateType):
    with (Session(models.engine) as session):
        series = get_all_manga_info(manga_title_eng)
        # series doesn't exist
        if series is None:
            logger.error("Series is not found")
            err_msg = f"error with updating read count for {manga_title_eng}"
            raise HTTPException(status_code=404, detail=err_msg)
        # series exists and assigning curr_read and total based on mark_type
        match mark_type:
            case models.MarkType.chapter:
                logger.info("mark type chapter")
                curr_read = series.chapters_read
                total = series.chapters_total
                logger.info("current read is %s", curr_read)
                logger.info("total is %s", total)

                # checking that not attempting to unread a series with a 0 curr_read value or read a series already
                # finished
                if (update_type is models.UpdateType.unread and curr_read - 1 < 0) or (
                        update_type is models.UpdateType.read and total != 0 and curr_read + 1 > total):
                    err_msg = f"error with updating read count for {manga_title_eng}"
                    raise HTTPException(status_code=404, detail=err_msg)

                else:
                    # updating mark type based on update_type
                    match update_type:
                        case models.UpdateType.read:
                            logger.info("marking as read")
                            i = curr_read + 1
                        case models.UpdateType.unread:
                            logger.info("marking as unread")
                            i = curr_read - 1
                    logger.info(i)
                    series.chapters_read = i
                    series.last_edited = datetime.now(timezone.utc)
                    session.add(series)
                    logger.info("added series")

            case models.MarkType.volume:
                logger.info("mark type volume")
                curr_read = series.volumes_read
                total = series.volumes_total
                logger.info("current read is %s", curr_read)
                logger.info("total is %s", total)

                # checking that not attempting to unread a series with a 0 curr_read value or read a series already
                # finished
                if (update_type is models.UpdateType.unread and curr_read - 1 < 0) or (
                        update_type is models.UpdateType.read and total != 0 and curr_read + 1 > total):
                    err_msg = f"error with updating read count for {manga_title_eng}"
                    raise HTTPException(status_code=404, detail=err_msg)

                else:
                    # updating mark type based on update_type
                    match update_type:
                        case models.UpdateType.read:
                            logger.info("marking as read")
                            i = curr_read + 1
                        case models.UpdateType.unread:
                            logger.info("marking as unread")
                            i = curr_read - 1
                    logger.info(i)
                    series.volumes_read = i
                    series.last_edited = datetime.now(timezone.utc)
                    session.add(series)
                    logger.info("added series")

        session.commit()
        session.refresh(series)
        return series
