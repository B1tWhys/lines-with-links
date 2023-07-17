import logging
from abc import ABC, abstractmethod
from functools import cached_property, cache
from multiprocessing import current_process, Queue
# from queue import Queue
from typing import Optional

import cv2
from PIL import Image
from yt_dlp import YoutubeDL

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
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def channel_url(self) -> str:
        pass

    @property
    @abstractmethod
    def thumbnail_url(self) -> str:
        pass

    @property
    @abstractmethod
    def views(self) -> int:
        pass

    @property
    @abstractmethod
    def channel_id(self) -> str:
        pass

    @property
    def current_sec_into_video(self) -> float:
        return self.current_frame / self.fps

    def stream_frames(self, stop_after_frames: Optional[int] = None) -> None:
        """
        Stream the video source into PIL images. Blocks until complete, and outputs to `self.img_output_queue`
        """
        try:
            cap = cv2.VideoCapture(self._source)
            log.debug(f"hello from frame source in pid {current_process().pid}")
            if not cap.isOpened():
                exception = VideoProcessingException(f"Video capture failed to open: {self._source}")
                self.img_output_queue.put(exception)
                return

            log.debug(f"Opencv video capture opened for {self._source}")
            # while the video is open, the task is still going, and we haven't passed the `stop_after_frames` arg
            while cap.isOpened() and \
                    self.running and \
                    (stop_after_frames is None or self.current_frame < stop_after_frames):
                log.debug(f"frame source is working in pid {current_process().pid}")
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
    def __init__(self, video_url: str, resolution='480p', subtype='mp4'):
        super().__init__()
        self._url = video_url
        self._info = self.__get_vid_info()
        self._format = self.__find_format(resolution, subtype)

    def __get_vid_info(self):
        ytdl_opts = {"quiet": True}
        with YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(self._url, download=False)
            return ydl.sanitize_info(info)

    def __find_format(self, resolution, subtype):
        formats = self._info['formats']
        for fmt in formats:
            if fmt.get('format_note', '') == resolution and fmt.get('ext', '') == subtype:
                return fmt
        else:
            raise VideoProcessingException(f"Failed to process {self._info['id']}, no worthy streams found. "
                                           f"Available streams were: {[f['format'] for f in formats]}")

    @cache
    def __len__(self):
        return self._info['duration']

    @cached_property
    def _source(self) -> str:
        return self._format['url']

    @cached_property
    def fps(self) -> float:
        return self._format['fps']

    @cached_property
    def video_id(self) -> str:
        return self._info['id']

    @cached_property
    def title(self) -> str:
        return self._info['title']

    @property
    def channel_url(self) -> str:
        return self._info['channel_url']

    @property
    def thumbnail_url(self) -> str:
        return self._info['thumbnail']

    @property
    def views(self) -> int:
        return self._info['view_count']

    @property
    def channel_id(self):
        return self._info['channel_id']


class FileFrameSource(FrameSource):
    """
    Only used in tests
    """

    @property
    def channel_id(self) -> str:
        return "test-channel"

    @property
    def channel_url(self) -> str:
        return "http://example.com"

    @property
    def thumbnail_url(self) -> str:
        return "http://example.com"

    @property
    def views(self) -> int:
        pass

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

    @property
    def title(self) -> str:
        return self.file_path
