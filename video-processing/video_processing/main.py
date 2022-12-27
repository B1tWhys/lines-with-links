import pytube

from video_processing.position_extraction import extract_fen
from video_processing.db import *
import logging
import typer

logging.basicConfig(level=logging.INFO)
logging.getLogger('video_processing').setLevel(logging.INFO)
log = logging.getLogger('video_processing.main')
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

    fen_timestamps = extract_fen(yt)

    for fen, timestamps in fen_timestamps.items():
        for timestamp in timestamps:
            save_position_sighting(yt.video_id, fen, round(timestamp, 2))

if __name__ == "__main__":
    app()
    # timestamps = process_yt_video("https://www.youtube.com/watch?v=vRAXtMOcnVI")
    # print(json.dumps(timestamps, indent=2))
