from sqlalchemy import (create_engine,
                        insert,
                        exists, Column, String, ForeignKey, Integer, Float, select)
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy.engine import Engine, URL, Row
import logging

log = logging.getLogger("video_processing.db")

_engine: Engine

Base = declarative_base()


class Channel(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True)
    channel_name = Column(String, nullable=False)

    videos = relationship("Video", back_populates="channel")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    channel_id = Column(ForeignKey("channels.id"))
    title = Column(String, nullable=False)
    thumbnail_url = Column(String)

    channel = relationship("Channel", back_populates="videos")
    positions = relationship("Position", secondary="position_sightings", back_populates="videos", viewonly=True)
    position_sightings = relationship("PositionSighting", back_populates="video")


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    fen = Column(String, nullable=False, index=True, unique=True)

    videos = relationship("Video", secondary="position_sightings", back_populates="positions", viewonly=True)
    sightings = relationship("PositionSighting", back_populates="position")


class PositionSighting(Base):
    __tablename__ = "position_sightings"

    id = Column(Integer, primary_key=True)
    video_id = Column(ForeignKey("videos.id"))
    position_id = Column(ForeignKey("positions.id"))
    sec_into_video = Column(Float, nullable=False)

    position = relationship("Position", back_populates="sightings")
    video = relationship("Video", back_populates="position_sightings")


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
    Base.metadata.create_all(_engine)
    log.debug("DB configured")


def save_channel(id: str, channel_name: str):
    with Session(_engine) as session:
        if session.get(Channel, id) is None:
            log.info(f"Persisting new channel: {id}")
            session.add(Channel(id=id, channel_name=channel_name))
            session.commit()


def save_video(video_id: str, channel_id: str, title: str, thumbnail_url: str):
    with Session(_engine) as session:
        if session.get(Video, video_id) is None:
            channel: Channel = session.get(Channel, channel_id)
            video = Video(id=video_id, title=title, thumbnail_url=thumbnail_url)
            channel.videos.append(video)
            session.commit()


def save_position_sighting(video_id: str, fen: str, sec_into_video: float):
    with Session(_engine) as session:
        pos_row: Position | None = session.execute(select(Position).where(Position.fen == fen)).scalars().one_or_none()
        sighting: PositionSighting = PositionSighting(video_id=video_id, sec_into_video=sec_into_video)
        if pos_row is None:
            pos_row = Position(fen=fen)
            pos_row.sightings.append(sighting)
            session.add(pos_row)
        else:
            pos_row.sightings.append(sighting)
        session.commit()
