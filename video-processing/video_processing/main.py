import pytube
from video_processing.data_loading import YoutubeFrameSource
import logging
import typer
from video_processing.db import init_sqlite_db, init_db, save_video, save_channel
from threading import Thread
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from multiprocessing.pool import ThreadPool as Pool

from video_processing.video_processing_task import VideoProcessingTask

logging.basicConfig(level=logging.INFO)
logging.getLogger('video_processing')
log = logging.getLogger('video_processing')
log.setLevel(logging.INFO)

app = typer.Typer()
in_progress_tasks = set()


def video_processing_task_wrapper(vid_url: str):
    frame_source = YoutubeFrameSource(vid_url)
    vid = frame_source.yt_video
    log.info(f"Starting processing {vid.title}")
    save_video(vid.video_id, vid.channel_id, vid.title, vid.thumbnail_url)

    with tqdm(total=len(frame_source), smoothing=.2) as bar:
        bar.set_description(frame_source.video_id)
        task = VideoProcessingTask(frame_source, lambda: bar.update(1))
        in_progress_tasks.add(task)
        task.run()
        in_progress_tasks.remove(task)


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


@app.command()
def channel(url: str,
            threads: int,
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

    channel = pytube.Channel(url)
    save_channel(channel.channel_id, channel.channel_name, channel.channel_url)
    log.info(f"Loading video list for {channel.channel_name}...")
    video_urls = list(channel.video_urls)
    with logging_redirect_tqdm():
        with tqdm(total=len(video_urls), smoothing=0) as channel_bar:
            channel_bar.set_description(channel.channel_name)
            with Pool(threads) as pool:
                video_processing_task_completions = pool.imap(video_processing_task_wrapper, video_urls)
                try:
                    log.info("All tasks have been queued...")
                    for _ in video_processing_task_completions:
                        channel_bar.update(1)
                except KeyboardInterrupt:
                    log.info("Closing pool and stopping in-progress tasks")
                    pool.terminate()
                    for task in in_progress_tasks:
                        task.stop()
                    log.info("Waiting for remaining tasks to exit")
                    pool.join()


if __name__ == "__main__":
    app()
