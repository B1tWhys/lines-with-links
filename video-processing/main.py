from video_processing.position_extraction import process_yt_video
import logging
import json

logging.basicConfig(level=logging.INFO)
logging.getLogger('video_processing').setLevel(logging.DEBUG)


if __name__ == "__main__":
    timestamps = process_yt_video("https://www.youtube.com/watch?v=vRAXtMOcnVI")
    print(json.dumps(timestamps, indent=2))