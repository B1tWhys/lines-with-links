from PIL import Image
from .tensorflow.tensorflow_chessbot import ChessboardPredictor
from .tensorflow.helper_functions import shortenFEN, unflipFEN, predictSideFromFEN
from pytube import YouTube
import cv2
import logging
from collections import defaultdict

log = logging.getLogger('video_processing')
predictor = ChessboardPredictor()

class VideoProcessingException(Exception):
    pass


def extract_position(img: Image) -> str | None:
    fen, certainty = predictor.makePrediction(img)
    if fen is None:
        return None
    side = predictSideFromFEN(fen)
    if side == 'b':
        fen = unflipFEN(fen)
    return shortenFEN(fen)


def process_yt_video(url: str) -> dict[str, list[str]]:
    stream_url, fps = _resolve_download_url(url)
    log.debug(f"Stream selected for video {url}: {stream_url}")

    result = defaultdict(list)
    prev_fen = None
    for frameNum, pil_frame in enumerate(stream_pil_images(stream_url)):
        sec_into_video = frameNum / fps
        fen = extract_position(pil_frame)
        if fen is None:
            log.debug(f"No fen found at {frameNum} ({sec_into_video}s), skipping frame")
            continue
        if fen != prev_fen:
            log.debug(f"New position found at {frameNum} ({sec_into_video}s)")
            result[fen].append(sec_into_video)
            prev_fen = fen
    return result



def _resolve_download_url(vid_url):
    yt = YouTube(vid_url)
    stream = yt.streams.filter(only_video=True, res='480p', subtype="mp4").first()
    if stream is None:
        raise VideoProcessingException(f"Failed to process {vid_url}, no streams found. Available streams were: {yt.streams}")
    return stream.url, stream.fps

def stream_pil_images(stream_url):
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        raise VideoProcessingException(f"Video capture failed to open url: {stream_url}")
    log.debug(f"Opencv video capture opened")
    while cap.isOpened():
        ret, cv2_img = cap.read()
        if ret:
            converted = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
            pil_im = Image.fromarray(converted)
            yield pil_im
        else:
            break
    cap.release()
