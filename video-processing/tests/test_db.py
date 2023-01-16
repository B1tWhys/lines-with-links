import pytest
from typer.testing import CliRunner
from video_processing.db import *

runner = CliRunner()


class TestPersistence:
    def test_extracted_data_is_persisted(self, in_mem_db: Engine, mocker):
        # mock position extraction function
        test_fen1 = "2kr3r/ppp2pp1/5n1p/4n1N1/2Pqp1b1/3P2P1/P1PQ1PBP/1RB2RK1"
        test_fen2 = "8/1pq2ppk/r1p1nn1p/p1b1p3/P1N1P1BP/2P1B1P1/1P2QPK1/3R4"
        extracted_data = []
        for i in range(4):
            extracted_data.append((test_fen1, float(i)))
        for i in range(4):
            extracted_data.append((test_fen2, float(i)))
        mocker.patch("video_processing.tensorflow.frame_analyzer.extract_fen", return_value=extracted_data)

        from video_processing import main

        result = runner.invoke(main.app,
                      ["video", "https://www.youtube.com/watch?v=TsR154sQMVo", "--sqlite-db", "--db-password", "foo"])
        if result.exception:
            raise result.exception

        with Session(in_mem_db) as session:
            saved_channel: Channel = session.get(Channel, "UCweCc7bSMX5J4jEH7HFImng")
            assert saved_channel is not None

            vids = saved_channel.videos
            assert len(vids) == 1
            saved_video = session.get(Video, "TsR154sQMVo")
            assert saved_video is not None
            assert saved_video.channel.id == saved_channel.id

            assert len(saved_video.positions) == 2
            assert len(saved_video.position_sightings) == 8

            saved_position = session.execute(select(Position).where(Position.fen == test_fen1)).scalars().one()
            assert len(saved_position.sightings) == 4

            assert saved_video.views > 0
            assert saved_video.length > 0

            assert all_processed_video_ids() == ['TsR154sQMVo']



@pytest.fixture
def in_mem_db():
    return init_sqlite_db()
