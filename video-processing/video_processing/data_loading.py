import logging
from abc import ABC, abstractmethod
from functools import cached_property, cache
from queue import Queue

import cv2
from PIL import Image
from pytube import YouTube, Stream

log = logging.getLogger(__name__)


class VideoProcessingException(Exception):
    pass


class FrameSource(ABC):
    """
    Abstract strategy class for streaming a video as a series of PIL Images
    """

    current_frame: int
    img_output_queue: Queue
    running: bool

    def __init__(self):
        self.current_frame = 0
        self.img_output_queue = Queue(30)
        self.running = True

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

    @property
    @abstractmethod
    def video_id(self) -> str:
        pass

    @property
    def current_sec_into_video(self) -> float:
        return self.current_frame / self.fps

    def stream_frames(self) -> None:
        """
        Stream the video source into PIL images
        :param source: A string of either a file path, or a URL to download the video from
        """
        try:
            cap = cv2.VideoCapture(self._source)
            # print(f"hello from frame source in pid {current_process().pid}")
            if not cap.isOpened():
                exception = VideoProcessingException(f"Video capture failed to open: {self._source}")
                self.img_output_queue.put(exception)
                return

            log.debug(f"Opencv video capture opened for {self._source}")
            while cap.isOpened() and self.running:
                # print(f"frame source is working in pid {current_process().pid}")
                ret, cv2_img = cap.read()
                if ret:
                    self.current_frame += 1
                    converted = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
                    pil_im = Image.fromarray(converted)
                    self.img_output_queue.put(pil_im)
                else:
                    break
        finally:
            # cap.release()
            self.img_output_queue.put(None)


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
        return self.yt_video.length * self.fps

    @cached_property
    def _source(self) -> str:
        return self._stream.url

    @cached_property
    def fps(self) -> float:
        return self._stream.fps

    @cached_property
    def video_id(self) -> str:
        return self.yt_video.video_id


class FileFrameSource(FrameSource):
    """
    Only used in tests
    """
    file_path: str

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def __len__(self) -> int:
        cap = cv2.VideoCapture(self._source)
        return int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def _source(self) -> str:
        return self.file_path

    @property
    def fps(self):
        return 30

    @property
    def video_id(self) -> str:
        return "testvideo"
