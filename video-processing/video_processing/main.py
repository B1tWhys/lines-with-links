import dataclasses

import pytube
from video_processing.data_loading import YoutubeFrameSource, FrameSource
from video_processing.tensorflow.frame_analyzer import frame_analysis_worker, Frame, FenExtractionResult
import logging
import typer
from video_processing.db import init_sqlite_db, init_db, save_video, save_channel, save_position_sighting
from queue import Queue, Empty
from threading import Thread

logging.basicConfig(level=logging.INFO)
logging.getLogger('video_processing')
log = logging.getLogger('video_processing')
log.setLevel(logging.DEBUG)

app = typer.Typer()

frame_source_queue = Queue()
frames_queue = Queue(30)
extraction_result_queue = Queue()


def clear_queue(q):
    while True:
        try:
            q.get_nowait()
        except Empty:
            break


def video_streaming_worker():
    log.info("Starting video streaming worker")
    while True:
        frame_source: FrameSource = frame_source_queue.get()
        if frame_source is None:
            break
        for img in frame_source.stream_frames():
            frame = Frame(frame_source.video_id, img, frame_source.current_sec_into_video)
            log.info(f"Frame received: {frame.sec_into_video:0.2f}")
            frames_queue.put(frame)
    log.info("Video streaming worker exiting...")

def position_persistance_worker():
    log.info("Starting persistance worker")
    while True:
        result: FenExtractionResult = extraction_result_queue.get()
        if result is None:
            break
        log.debug(f"extracted result: {result}")
        save_position_sighting(result.vid_id, result.fen, result.sec_into_video)


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
    frame_source_queue.put(None)

    frame_analyzer_thread, stream_thread, position_persistance_thread = initialize_threads()

    try:
        stream_thread.join()
        log.info("Stream thread done")
        frame_analyzer_thread.join()
        log.info("Frame analyzer done")
        extraction_result_queue.put(None)
        position_persistance_thread.join()
        log.info("Last positions persisted")
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt received, cleaning up workers...")

        clear_queue(frame_source_queue)
        frame_source_queue.put(None)
        log.debug("frame_source_queue cleared")

        clear_queue(frames_queue)
        frames_queue.put(None)
        log.debug("frames_queue cleared")

        stream_thread.join()


def initialize_threads():
    stream_thread = Thread(target=video_streaming_worker)
    frame_analyzer_thread = Thread(target=frame_analysis_worker, args=[frames_queue, extraction_result_queue])
    position_persistence_thread = Thread(target=position_persistance_worker)
    stream_thread.start()
    frame_analyzer_thread.start()
    position_persistence_thread.start()
    return frame_analyzer_thread, stream_thread, position_persistence_thread


if __name__ == "__main__":
    app()
