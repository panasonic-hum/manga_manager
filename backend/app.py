from fastapi import FastAPI, Query, HTTPException, Depends, status
import models
from sqlmodel import Session, select
from typing import Annotated
from logging.config import dictConfig
import logging
from app_logger import LogConfig
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from pathlib import Path

dictConfig(LogConfig().dict())
logger = logging.getLogger("manga_manager")
dotenv_path = Path('MALlists.env')
load_dotenv(dotenv_path=dotenv_path)
SECRET_KEY: str = os.getenv('SECRET_KEY')
ALGORITHM: str = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.on_event("startup")
def startup():
    models.create_db_and_tables()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    with Session(models.engine) as session:
        user_row = session.exec(
            select(models.User)
            .where(models.User.username == username)
        ).one_or_none()
        return user_row


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = models.TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[models.User, Depends(get_current_user)],
):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_user(username: str, password: str, full_name: str):
    with Session(models.engine) as session:
        hashedpass = get_password_hash(password)
        user = models.User(username=username, full_name=full_name, active=True, hashed_password=hashedpass)
        session.add(user)
        session.commit()


@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> models.Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return models.Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=models.User)
async def read_users_me(
        current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/mangamanager/lists/all")
def all_mangalists(current_user: Annotated[models.User, Depends(get_current_active_user)]):
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.user_id == current_user.id)
        all_lists = session.exec(statement)
        return all_lists.all()


@app.get("/mangamanager/lists/reading")
def reading_mangalist(current_user: Annotated[models.User, Depends(get_current_active_user)]):
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 1).where(
            models.ReadingLists.user_id == current_user.id)
        currread_list = session.exec(statement)
        return currread_list.all()


@app.get("/mangamanager/lists/read")
def read_mangalist(current_user: Annotated[models.User, Depends(get_current_active_user)]):
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 2).where(
            models.ReadingLists.user_id == current_user.id)
        read_list = session.exec(statement)
        return read_list.all()


@app.get("/mangamanager/lists/onhold")
def onhold_mangalist(current_user: Annotated[models.User, Depends(get_current_active_user)]):
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 3).where(
            models.ReadingLists.user_id == current_user.id)
        onhold_list = session.exec(statement)
        return onhold_list.all()


@app.get("/mangamanager/lists/dropped")
def dropped_mangalist(current_user: Annotated[models.User, Depends(get_current_active_user)]):
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 4).where(
            models.ReadingLists.user_id == current_user.id)
        dropped_list = session.exec(statement)
        return dropped_list.all()


@app.get("/mangamanager/lists/plantoread")
def ptr_mangalist(current_user: Annotated[models.User, Depends(get_current_active_user)]):
    with Session(models.engine) as session:
        statement = select(models.ReadingLists).where(models.ReadingLists.status == 6).where(
            models.ReadingLists.user_id == current_user.id)
        ptr_list = session.exec(statement)
        return ptr_list.all()


@app.get("/mangamanager/manga_info/mark_total")
def get_mark_total(mark_type: models.MarkType, manga_title_eng: Annotated[str,
Query(description="manga title is case sensitive")],
                   current_user: Annotated[models.User, Depends(get_current_active_user)]):
    with Session(models.engine) as session:
        if mark_type is models.MarkType.chapter:
            chapter_total = session.exec(
                select(models.ReadingLists.chapters_total)
                .where(models.ReadingLists.manga_title_eng == manga_title_eng).where(
                    models.ReadingLists.user_id == current_user.id)
            ).one_or_none()
            return chapter_total
        elif mark_type is models.MarkType.volume:
            volume_total = session.exec(
                select(models.ReadingLists.volumes_total)
                .where(models.ReadingLists.manga_title_eng == manga_title_eng).where(
                    models.ReadingLists.user_id == current_user.id)
            ).one_or_none()
            return volume_total
        else:
            return "mark type didn't match"


@app.get("/mangamanager/manga_info/read_total")
def get_read_total(mark_type: models.MarkType, manga_title_eng: Annotated[str,
Query(description="manga title is case sensitive")],
                   current_user: Annotated[models.User, Depends(get_current_active_user)]):
    with Session(models.engine) as session:
        if mark_type is models.MarkType.chapter:
            chapter_total = session.exec(
                select(models.ReadingLists.chapters_read)
                .where(models.ReadingLists.manga_title_eng == manga_title_eng).where(
                    models.ReadingLists.user_id == current_user.id)
            ).one_or_none()
            return chapter_total
        elif mark_type is models.MarkType.volume:
            volume_total = session.exec(
                select(models.ReadingLists.volumes_read)
                .where(models.ReadingLists.manga_title_eng == manga_title_eng).where(
                    models.ReadingLists.user_id == current_user.id)
            ).one_or_none()
            return volume_total
        else:
            return "mark type didn't match"


@app.get("/mangamanager/manga_info/get_series", response_model=models.AllMangaInfo)
def get_all_manga_info(manga_title_eng: str, current_user: Annotated[models.User, Depends(get_current_active_user)]):
    with Session(models.engine) as session:
        manga = session.query(models.ReadingLists).where(models.ReadingLists.user_id == current_user.id).filter(
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


@app.patch("/mangamanager/update/update_rating", response_model=models.ScoreUpdate)
def update_rating(manga_title_eng: str, new_rating: int):
    with (Session(models.engine) as session):
        series = get_all_manga_info(manga_title_eng)
        # series doesn't exist
        if series is None:
            logger.error("Series is not found")
            err_msg = f"error with updating rating for {manga_title_eng}"
            raise HTTPException(status_code=404, detail=err_msg)
        else:
            series.score = new_rating
            session.add(series)
            session.commit()
            session.refresh(series)
            return series


@app.patch("/mangamanager/update/update_status", response_model=models.StatusUpdate)
def update_status(manga_title_eng: str, new_status: int):
    with (Session(models.engine) as session):
        series = get_all_manga_info(manga_title_eng)
        # series doesn't exist
        if series is None:
            logger.error("Series is not found")
            err_msg = f"error with updating status for {manga_title_eng}"
            raise HTTPException(status_code=404, detail=err_msg)
        elif new_status == 0 or new_status == 5 or new_status > 6:
            err_msg = "status is not valid"
            raise HTTPException(status_code=404, detail=err_msg)
        else:
            series.status = new_status
            session.add(series)
            session.commit()
            session.refresh(series)
            return series


@app.post("/mangamanager/update/read_log", response_model=models.ReadingLog)
def update_read_log(user_id: int, readinglists_id: int, mark_type: models.MarkType, update_type: models.UpdateType,
                    mark_value: int):
    with (Session(models.engine) as session):
        read_log = models.ReadingLog(user_id=user_id, readinglists_id=readinglists_id, mark_type=mark_type,
                                     update_type=update_type, mark_value=mark_value)
        session.add(read_log)
        session.commit()
        session.refresh(read_log)
        return read_log
