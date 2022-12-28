import pytube

from video_processing.position_extraction import process_video
from video_processing.db import *
import logging
import typer
from tqdm.contrib.logging import logging_redirect_tqdm
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logging.getLogger('video_processing')
log = logging.getLogger('video_processing')
log.setLevel(logging.DEBUG)

app = typer.Typer()


@app.command()
def process(url: str,
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

    yt = pytube.YouTube(url)
    pt_channel = pytube.Channel(yt.channel_url)
    save_channel(pt_channel.channel_id, pt_channel.channel_name, pt_channel.channel_url)
    save_video(yt.video_id, pt_channel.channel_id, yt.title, yt.thumbnail_url)

    with logging_redirect_tqdm():
        fen_timestamps = process_video(yt)
        with tqdm(total=yt.length, smoothing=0) as bar:
            for fen, timestamp in fen_timestamps:
                log.debug(f"saving position {fen} : {timestamp:0.3f}")
                save_position_sighting(yt.video_id, fen, round(timestamp, 2))
                bar.update(timestamp - bar.n)


    if __name__ == "__main__":
        app()
