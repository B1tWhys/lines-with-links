import dataclasses

import pytube
from PIL import Image
from video_processing.data_loading import YoutubeFrameSource, FrameSource
import logging
import typer
from video_processing.db import init_sqlite_db, init_db, save_video, save_channel
from queue import Queue, Empty
from threading import Thread

logging.basicConfig(level=logging.INFO)
logging.getLogger('video_processing')
log = logging.getLogger('video_processing')
log.setLevel(logging.DEBUG)

app = typer.Typer()

frame_source_queue = Queue()
frames_queue = Queue(30)
running = True


@dataclasses.dataclass
class Frame:
    vid_id: str
    img: Image.Image
    sec_into_video: float


def empty_queue(q):
    while True:
        try:
            q.get_nowait()
        except Empty:
            break


def video_streaming_worker():
    log.info("Starting video streaming worker")
    while running:
        frame_source: FrameSource = frame_source_queue.get()
        if frame_source is None:
            break
        for img in frame_source.stream_frames():
            frame = Frame(frame_source.video_id, img, frame_source.current_sec_into_video)
            log.info(f"Frame received: {frame.sec_into_video:0.2f}")
            frames_queue.put(frame)
    log.info("Video streaming worker exiting...")


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

    frame_source_queue.put(frame_source)

    stream_thread = Thread(target=video_streaming_worker)
    try:
        stream_thread.start()
        stream_thread.join()
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt received, cleaning up workers...")

        global running
        running = False
        empty_queue(frame_source_queue)
        frame_source_queue.put(None)
        log.debug("frame_source_queue cleared")
        empty_queue(frames_queue)
        log.debug("frames_queue cleared")
        stream_thread.join()

if __name__ == "__main__":
    app()
