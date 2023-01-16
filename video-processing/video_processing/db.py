import logging

from sqlalchemy import (create_engine,
                        Column, String, ForeignKey, Integer, Float, select)
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import Session, declarative_base, relationship

log = logging.getLogger("video_processing")

_engine: Engine

Base = declarative_base()


class Channel(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True)
    channel_name = Column(String, nullable=False)
    channel_url = Column(String, nullable=False)

    videos = relationship("Video", back_populates="channel")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    channel_id = Column(ForeignKey("channels.id"))
    title = Column(String, nullable=False)
    thumbnail_url = Column(String)
    views = Column(Integer)
    length = Column(Float)

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
    the schema from scratch. The sqlite db is created on disk at ./testdata.sqlite

    must be called from the main process

    :return: A sqlalchemy Engine (for use in tests)
    """
    global _engine
    log.info("Initializing fresh sqlite DB at ./testdata.sqlite")
    _engine = create_engine("sqlite+pysqlite:///testdata.sqlite")
    metadata = Base.metadata
    metadata.drop_all(_engine)
    metadata.create_all(_engine)
    log.debug("sqlite DB bootstrapped successfully")
    return _engine


def init_postgres_db(hostname, port, username, password, dbname):
    """
    Connect to a postgres DB, and create the necessary tables (if they aren't there already)

    must be called from the main process

    :param hostname: hostname to connect to
    :param port: port to connect to
    :param username: username for signing in to the DB
    :param password: password for signing in to the DB
    :param dbname: the logical database to use
    :return: None
    """
    global _engine
    log.info(f"Connecting to db {hostname}:{port}")
    url = URL.create("postgresql+psycopg2",
                     username=username,
                     password=password,
                     host=hostname,
                     port=port,
                     database=dbname)
    _engine = create_engine(url)
    log.debug("Creating schema")
    Base.metadata.create_all(_engine)
    log.debug("postgres DB engine bootstrapped successfully")


def save_channel(id: str, channel_name: str, channel_url: str):
    """
    Persist a channel to the database if it doesn't already exist there. If the channel is already there,
    do nothing

    must be called from the main process

    :param id: channel id
    :param channel_name: channel name
    :param channel_url: channel url
    :return: None
    """
    with Session(_engine) as session:
        if session.get(Channel, id) is None:
            log.info(f"Persisting new channel: {id}")
            session.add(Channel(id=id, channel_name=channel_name, channel_url=channel_url))
            session.commit()


def save_video(video_id: str, channel_id: str, title: str, thumbnail_url: str, views: int, length: float):
    """
    Persist a video to the database if it isn't already there. If the video is there already then simply return

    must be called from the main process

    :param video_id: video id
    :param channel_id: id of the channel that posted the video
    :param title: title of the video
    :param thumbnail_url: url to load the thumbnail of the video
    :param views: current view count
    :param length: length of the video in seconds
    :return: None
    """
    with Session(_engine) as session:
        if session.get(Video, video_id) is None:
            channel: Channel = session.get(Channel, channel_id)
            video = Video(id=video_id, title=title, thumbnail_url=thumbnail_url, views=views, length=length)
            channel.videos.append(video)
            session.commit()


def save_position_sighting(video_id: str, fen: str, sec_into_video: float):
    """
    Persist a record of a position sighting to the database. The corresponding position and video records
    must already be there, otherwise a sqlalchemy IntegrityError is raised

    must be called from the main process

    :param video_id: id of the video where the position was observed
    :param fen: the fen containing the position
    :param sec_into_video: the number of seconds into the video where the position was observed
    :return: None
    """
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


def all_processed_video_ids() -> list[str]:
    """
    Get a list of all video id's in the database

    must be called from the main process

    :return: a list of all video id's
    """
    with Session(_engine) as session:
        ret = list(session.execute(select(Video.id)).scalars().all())
        log.debug(f"All {len(ret)} previously processed video id's received")
        return ret
