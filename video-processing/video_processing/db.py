from sqlalchemy import (create_engine,
                        insert,
                        exists, Column, String, ForeignKey, Integer, Float)
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy.engine import Engine, URL
import logging

log = logging.getLogger("video_processing.db")

_engine: Engine

Base = declarative_base()


class Channel(Base):
    __tablename__ = "channels"

    id = Column(String(16), primary_key=True)
    channel_name = Column(String, nullable=False)

    videos = relationship("Video", back_populates="channel")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String(16), primary_key=True)
    channel_id = Column(ForeignKey("channels.id"))
    title = Column(String, nullable=False)
    thumbnail_url = Column(String)

    channel = relationship("Channel", back_populates="videos")

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    fen = Column(String, nullable=False)
    sec_into_video = Column(Float, nullable=False)
    # video_id = Column(ForeignKey("videos.id"))


def init_sqlite_db() -> Engine:
    """
    Drops everything in a sqlite DB (if it already existed), and recreates
    the schema from scratch
    :return: A sqlalchemy Engine for use in tests
    """
    global _engine
    log.warning("Using in-memory DB!")
    _engine = create_engine("sqlite+pysqlite:///testdata.sqlite")
    metadata = Base.metadata
    metadata.drop_all(_engine)
    metadata.create_all(_engine)
    log.debug("In-memory DB configured")
    return _engine


def init_db(hostname, port, username, password, dbname):
    global _engine
    log.info(f"Connecting to db {hostname}:{port}")
    url = URL.create("postgresql+psycopg2",
                     username=username,
                     password=password,
                     host=hostname,
                     port=port,
                     database=dbname)
    _engine = create_engine(url)
    log.info("Creating schema (if necessary)")
    Base.metadata.create_all()
    log.debug("DB configured")


def save_channel(id: str, channel_name: str):
    with Session(_engine) as session:
        if session.get(Channel, id) is None:
            session.add(Channel(id=id, channel_name=channel_name))
            session.commit()

def save_video(video_id: str, channel_id: str, title: str, thumbnail_url: str):
    