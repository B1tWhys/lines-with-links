import pytube
import typer


def main(playlist_url: str):
    playlist = pytube.Playlist(playlist_url)
    for video in playlist.videos:
        print(video.watch_url)


if __name__ == '__main__':
    typer.run(main)
