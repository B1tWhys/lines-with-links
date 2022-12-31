import pytube

from video_processing.data_loading import YoutubeFrameSource
from video_processing.db import *
import logging
import typer
from tqdm.contrib.logging import logging_redirect_tqdm
from tqdm import tqdm
from multiprocessing.pool import ThreadPool as Pool

logging.basicConfig(level=logging.INFO)
logging.getLogger('video_processing')
log = logging.getLogger('video_processing')
log.setLevel(logging.DEBUG)

app = typer.Typer()


def process_yt_vid(url):
    frame_source = YoutubeFrameSource(url)
    vid = frame_source.yt_video
    log.info(f"Processing video: {vid.title}")
    save_video(vid.video_id, vid.channel_id, vid.title, vid.thumbnail_url)
    # with tqdm(total=len(frame_source), smoothing=0) as bar:
    #     try:
    #         bar.set_description(vid.video_id)
    #         for fen, timestamp in process_video(vid):
    #             log.debug(f"saving position {fen} : {timestamp:0.3f}")
    #             save_position_sighting(vid.video_id, fen, round(timestamp, 2))
    #             bar.update(timestamp - bar.n)
    #     except Exception as e:
    #         log.warning(f"Failed to process video: {vid.video_id}", e)
    #         with open('./failed_videos.txt', 'a') as f:
    #             f.write(vid.video_id + '\n')
    # return None


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

    vid = pytube.YouTube(url)
    pt_channel = pytube.Channel(vid.channel_url)
    save_channel(pt_channel.channel_id, pt_channel.channel_name, pt_channel.channel_url)

    with logging_redirect_tqdm():
        process_yt_vid(vid)

#
# @app.command()
# def channel(url: str,
#             db_hostname: str = typer.Option("localhost", envvar="DB_HOSTNAME"),
#             db_username: str = typer.Option("postgres", envvar="DB_USERNAME"),
#             db_password: str = typer.Option(..., prompt=True, hide_input=True, envvar="DB_PASSWORD"),
#             db_port: int = typer.Option(default=5432, envvar="DB_PORT"),
#             db_name: str = typer.Option("postgres", envvar="DB_NAME"),
#             sqlite_db: bool = typer.Option(False),
#             threads: int = 5):
#     if sqlite_db:
#         init_sqlite_db()
#     else:
#         init_db(db_hostname, db_port, db_username, db_password, db_name)
#
#     pt_channel = pytube.Channel(url)
#     log.info(f"Processing videos on channel: {pt_channel.channel_name}")
#     save_channel(pt_channel.channel_id, pt_channel.channel_name, pt_channel.channel_url)
#
#     log.debug(f"Fetching list of videos...")
#     all_vids = pt_channel.videos
#     log.debug("Filtering them...")
#     already_processed = set(all_processed_video_ids())
#     vid_urls = [v.watch_url for v in all_vids if v.video_id not in already_processed]
#
#     with logging_redirect_tqdm():
#         with Pool(threads) as p:
#             # for v in tqdm(vids):
#             #     process_vid(v)
#             list(tqdm(p.imap(process_yt_vid, vid_urls), total=pt_channel.length))


if __name__ == "__main__":
    app()
