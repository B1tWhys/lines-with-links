from PIL import Image
from .tensorflow.tensorflow_chessbot import ChessboardPredictor
from .tensorflow.helper_functions import shortenFEN, unflipFEN, predictSideFromFEN
from pytube import YouTube
import cv2
import logging
from typing import Generator, Tuple

log = logging.getLogger('video_processing')
predictor = ChessboardPredictor()


class VideoProcessingException(Exception):
    pass


def process_video(yt: YouTube, required_position_duration_frames=10) -> Generator[Tuple[str, float], None, None]:
    stream_url, fps = _resolve_download_url(yt)
    log.info(f"Stream selected for video {yt.video_id}: {stream_url}")

    prev_fen = None
    position_history = [None] * required_position_duration_frames
    for frameNum, pil_frame in enumerate(stream_pil_images(stream_url)):
        sec_into_video = frameNum / fps
        fen = _extract_position(pil_frame)
        position_history = position_history[1:] + [fen]
        if len(set(position_history)) == 1:
            if fen is None:
                log.debug(f"No fen found at {frameNum} ({sec_into_video}s), skipping frame")
                continue
            if fen != prev_fen and len(set(position_history)) == 1:
                log.debug(f"New position found at {frameNum} ({sec_into_video:0.3f}s)")
                prev_fen = fen
                yield fen, sec_into_video

def _extract_position(img: Image) -> str | None:
    fen, certainty = predictor.makePrediction(img)
    if fen is None:
        return None
    side = predictSideFromFEN(fen)
    if side == 'b':
        fen = unflipFEN(fen)
    return shortenFEN(fen)



def _resolve_download_url(yt: YouTube):
    stream = yt.streams.filter(only_video=True, res='480p', subtype="mp4").first()
    if stream is None:
        raise VideoProcessingException(f"Failed to process {yt.video_id}, no worthy streams found. "
                                       f"Available streams were: {yt.streams}")
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
