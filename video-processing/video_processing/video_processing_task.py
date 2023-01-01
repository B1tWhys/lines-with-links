from queue import Queue
from video_processing.data_loading import FrameSource
from threading import Thread
from video_processing.db import save_position_sighting
from video_processing.tensorflow.frame_analyzer import extract_fen
from typing import Callable
import logging

log = logging.getLogger(__name__)

class VideoProcessingTask:
    frame_img_queue: Queue
    frame_source: FrameSource
    _streaming_thread: Thread
    _frame_processed_callback: Callable[[], None]
    running: bool

    def __init__(self, frame_source: FrameSource, frame_processed_callback: Callable[[], None] = None):
        self.frame_img_queue = frame_source.img_output_queue
        self.frame_source = frame_source
        self._streaming_thread = Thread(target=frame_source.stream_frames)
        self.running = True
        self._frame_processed_callback = frame_processed_callback

    @property
    def video_id(self):
        return self.frame_source.video_id
    def run(self):
        self._streaming_thread.start()

        prev_fen = None
        fen_history = [None] * 10
        frame_num = 0

        while self.running:
            frame = self.frame_img_queue.get()
            frame_num += 1
            sec_into_video = (frame_num - 10) / self.frame_source.fps
            if frame is None:
                # video is over
                return

            if self._frame_processed_callback is not None:
                self._frame_processed_callback()

            fen = extract_fen(frame)
            fen_history = fen_history[1:] + [fen]

            if fen is None:
                log.debug(f"{self.video_id}: No position for frame {frame_num} ({sec_into_video:0.3f}s), skipping")
                continue

            log.debug(f"{self.video_id}: Fen detected on frame {frame_num} ({sec_into_video:0.3f}s): {fen}")

            # If the position hasn't changed, don't record a new position
            if fen == prev_fen:
                continue

            # If this position hasn't been on screen long enough, don't do anything
            if len(set(fen_history)) > 1:
                log.debug(f"{self.video_id}: Skipping {frame_num} because fen hasn't been around long enough yet")
                continue

            prev_fen = fen
            save_position_sighting(self.frame_source.video_id, fen, sec_into_video)

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.frame_source.running = False
