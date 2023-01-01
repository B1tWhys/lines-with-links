import pytube
from video_processing.data_loading import YoutubeFrameSource, FrameSource
from video_processing.tensorflow.frame_analyzer import Frame, FenExtractionResult
import logging
import typer
from video_processing.db import init_sqlite_db, init_db, save_video, save_channel, save_position_sighting
from queue import Queue, Empty
from threading import Thread
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from video_processing.video_processing_task import VideoProcessingTask

logging.basicConfig(level=logging.INFO)
logging.getLogger('video_processing')
log = logging.getLogger('video_processing')
log.setLevel(logging.DEBUG)

app = typer.Typer()

@app.command()
def video(url: str,
          db_hostname: str = typer.Option("localhost", envvar="DB_HOSTNAME"),
          db_username: str = typer.Option("postgres", envvar="DB_USERNAME"),
          db_password: str = typer.Option(..., prompt=True, hide_input=True, envvar="DB_PASSWORD"),
          db_port: int = typer.Option(default=5432, envvar="DB_PORT"),
          db_name: str = typer.Option("postgres", envvar="DB_NAME"),
          sqlite_db: bool = typer.Option(False)):
    if sqlite_db:
        init_sqlite_db()
    else:
        init_db(db_hostname, db_port, db_username, db_password, db_name)

    frame_source = YoutubeFrameSource(url)
    vid = frame_source.yt_video
    log.info(f"Processing video: {vid.title}")
    channel = pytube.Channel(vid.channel_url)
    save_channel(channel.channel_id, channel.channel_name, channel.channel_url)
    save_video(vid.video_id, vid.channel_id, vid.title, vid.thumbnail_url)

    with logging_redirect_tqdm():
        with tqdm(total=len(frame_source)) as bar:
            bar.set_description(frame_source.video_id)
            task = VideoProcessingTask(frame_source, lambda: bar.update(1))
            worker_thread = Thread(target=task.run)
            worker_thread.start()

            try:
                worker_thread.join()
            except KeyboardInterrupt:
                log.info("Canceling worker task...")
                task.stop()
                worker_thread.join()


if __name__ == "__main__":
    app()
