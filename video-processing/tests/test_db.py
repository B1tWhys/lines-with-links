import pytest
import logging
from sqlalchemy import text, func, select

from video_processing.db import *

# logging.getLogger("video_processing").setLevel(logging.DEBUG)
log = logging.getLogger("video_processing.tests")

class TestPersistence:
    def test_can_upsert_channel(self, in_mem_db: Engine):
        with Session(in_mem_db) as session:
            result = session.execute(select(Channel)).first()
            assert result is None

            save_channel("chan-id", "chan-name")
            saved_channel: Channel = session.get(Channel, "chan-id")
            assert saved_channel.id == "chan-id"
            assert saved_channel.channel_name == "chan-name"

            save_channel("chan-id", "chan-name")
            assert session.query(func.count()).first()[0] == 1

    def test_can_upsert_video(self, in_mem_db: Engine):
        with Session(in_mem_db):
            save_channel("chan-id", "chan-name")
            save_video(video_id="vid-id", channel_id="chan-id", title="title", thumbnail_url="thmb")


@pytest.fixture
def in_mem_db():
    return init_sqlite_db()
