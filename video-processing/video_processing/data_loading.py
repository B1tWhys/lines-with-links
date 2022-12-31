from abc import ABC, abstractmethod
from typing import Generator
from PIL import Image
import cv2
import logging
from pytube import YouTube, Stream
from functools import cached_property, cache

log = logging.getLogger(__name__)


class VideoProcessingException(Exception):
    pass


class FrameSource(ABC):
    """
    Abstract strategy class for streaming a video as a series of PIL Images
    """

    current_frame: int

    def __init__(self):
        self.current_frame = 0

    @abstractmethod
    def __len__(self):
        """
        Length of the video in frames
        """
        pass

    @property
    @abstractmethod
    def _source(self) -> str:
        pass

    @property
    @abstractmethod
    def fps(self) -> float:
        pass

    def stream_frames(self) -> Generator[Image.Image, None, None]:
        """
        Stream the video source into PIL images
        :param source: A string of either a file path, or a URL to download the video from
        """
        cap = cv2.VideoCapture(self._source)
        if not cap.isOpened():
            raise VideoProcessingException(f"Video capture failed to open: {self._source}")
        try:
            log.debug(f"Opencv video capture opened for {self._source}")
            while cap.isOpened():
                ret, cv2_img = cap.read()
                if ret:
                    self.current_frame += 1
                    converted = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
                    pil_im = Image.fromarray(converted)
                    yield pil_im
                else:
                    break
        finally:
            cap.release()


class YoutubeFrameSource(FrameSource):
    yt_video: YouTube
    _stream: Stream

    def __init__(self, video_url: str, resolution='480p', subtype='mp4'):
        super().__init__()
        self.yt_video = YouTube(video_url)
        self._stream = self.__find_stream(resolution, subtype)

    def __find_stream(self, resolution, subtype):
        stream = self.yt_video.streams.filter(only_video=True, res=resolution, subtype=subtype).first()
        if stream is None:
            raise VideoProcessingException(f"Failed to process {self.yt_video.video_id}, no worthy streams found. "
                                           f"Available streams were: {self.yt_video.streams}")
        return stream

    @cache
    def __len__(self):
        return self.yt_video.length

    @cached_property
    def _source(self) -> str:
        return self._stream.url

    @cached_property
    def fps(self) -> float:
        return self._stream.fps
