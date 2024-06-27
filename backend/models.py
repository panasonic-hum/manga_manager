from typing import Optional
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, create_engine, TIMESTAMP, text, Column, FetchedValue


class ReadingLists(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="User.id")
    status: int = Field(nullable=False)
    score: Optional[int]
    chapters_read: Optional[int] = None
    volumes_read: Optional[int] = None
    added_date: Optional[datetime]
    reading_start_date: Optional[datetime] = None
    reading_finished_date: Optional[datetime] = None
    manga_title: str = Field(nullable=False, unique=True)
    manga_title_eng: Optional[str]
    manga_title_localized: Optional[str]
    chapters_total: Optional[int] = None
    volumes_total: Optional[int] = None
    manga_pub_status: int = Field(nullable=False)
    mal_manga_id: int = Field(nullable=False)
    manga_url: Optional[str] = None
    manga_img_path: Optional[str] = None
    last_edited: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=FetchedValue(),
        ))


class MangaInfoId(SQLModel):
    id: int
    manga_title: str | None = None
    manga_title_eng: str | None = None


class MangaReadInfo(MangaInfoId):
    chapters_read: int | None = None
    volumes_read: int | None = None
    reading_start_date: datetime | None = None
    reading_finished_date: datetime | None = None
    chapters_total: int | None = None
    volumes_total: int | None = None


class AllMangaInfo(MangaReadInfo):
    status: int
    score: int | None = None
    added_date: datetime | None = None
    manga_title_localized: str | None = None
    manga_pub_status: int | None = None
    mal_manga_id: int | None = None
    manga_url: str | None = None
    manga_img_path: str | None = None


class MarkType(str, Enum):
    chapter = "chapter"
    volume = "volume"


class UpdateType(str, Enum):
    read = "read"
    unread = "unread"


class ReadUpdate(MangaInfoId):
    chapters_read: int | None = None
    volumes_read: int | None = None
    last_edited: datetime = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=FetchedValue(),
        ))


class ScoreUpdate(MangaInfoId):
    score: int | None = None
    last_edited: datetime = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=FetchedValue(),
        ))


class StatusUpdate(MangaInfoId):
    status: int | None = None
    last_edited: datetime = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=FetchedValue(),
        ))


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    full_name: str | None = None
    active: bool | None = None
    hashed_password: str


class UserInDB(User):
    hashed_password: str


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


class ReadingLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    readinglists_id: Optional[int] = Field(default=None, foreign_key="readinglists.id")
    mark_type: MarkType
    update_type: UpdateType
    mark_value: int
    updated_date: datetime = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=FetchedValue(),
        ))



sqlite_file_name = "manga_manager.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


