from pytube import YouTube

from .position_extraction import extract_fen
from .db import init_db, init_sqlite_db
import logging
import typer

logging.basicConfig(level=logging.INFO)
logging.getLogger('video_processing').setLevel(logging.DEBUG)
log = logging.getLogger('video_processing.main')

def process(url: str,
            db_hostname: str = typer.Option("localhost", envvar="DB_HOSTNAME"),
            db_username: str = typer.Option("postgres", envvar="DB_USERNAME"),
            db_password: str = typer.Option(..., prompt=True, hide_input=True, envvar="DB_PASSWORD"),
            db_port: int = typer.Option(default=5432, envvar="DB_PORT"),
            db_name: str = typer.Option("postgres", envvar="DB_NAME"),
            in_memory_db: bool = typer.Option(False)
            ):
    if in_memory_db:
        init_sqlite_db()
    else:
        init_db(db_hostname, db_port, db_username, db_password, db_name)

    yt = YouTube(url)
    fen_timestamps = extract_fen(yt)


def main():
    typer.run(process)


if __name__ == "__main__":
    main()
    # timestamps = process_yt_video("https://www.youtube.com/watch?v=vRAXtMOcnVI")
    # print(json.dumps(timestamps, indent=2))
