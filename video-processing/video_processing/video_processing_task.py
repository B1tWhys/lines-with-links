import logging
import multiprocessing as mp
import threading as thd
from pathlib import Path
from typing import Callable

import PIL.Image

from video_processing.data_loading import FrameSource
from video_processing.db import save_position_sighting
from video_processing.tensorflow.chessboard_finder import find_grayscale_tiles_in_image
from video_processing.tensorflow.frame_analyzer import process_tiles

log = logging.getLogger(__name__)


class TileStreamingException(Exception):
    img: PIL.Image.Image
    cause: Exception

    def __init__(self, img, cause):
        self.img = img
        self.cause = cause


def handle_failed_video(failed_img, failed_frame_num, failed_ts, video_id):
    msg = f"Failed to process frame {failed_frame_num} ({failed_ts:0.3f}s) from video {video_id}."
    if failed_img is not None:
        bad_img_dir = Path("./errors")
        bad_img_dir.mkdir(exist_ok=True)
        bad_img_path = bad_img_dir / f"{video_id}_{failed_frame_num}.png"
        failed_img.save(str(bad_img_path))
        msg += f"Failed frame persisted to: {str(bad_img_path)}"
    log.exception(msg)


class VideoProcessingTask:
    frame_source: FrameSource
    _frame_processed_callback: Callable[[], None]
    running: bool
    _tile_queue: mp.Queue

    def __init__(self, frame_source: FrameSource, frame_processed_callback: Callable[[], None] = None):
        self.frame_source = frame_source
        self.running = True
        self._tile_queue = mp.Queue(maxsize=30)
        self._frame_processed_callback = frame_processed_callback

    @property
    def video_id(self):
        return self.frame_source.video_id

    def _stream_cb_tile_tensors(self):
        """
        This function streams frames from the video, finds the chessboard in each frame (if there is one), and formats
          that section of the image appropriately for processing by the neural network. The resulting tensors are
          put on the _tile_queue rather than being returned directly

          This function is expected to be run in a forked process, sending the tensors back via self._tile_queue.
          This dramatically improves performance (compared to just running in another thread) by sidestepping the GIL
        """
        try:
            streaming_thread = thd.Thread(target=self.frame_source.stream_frames)
            streaming_thread.start()

            img_queue = self.frame_source.img_output_queue
            while True:
                img = img_queue.get()
                if img is None:
                    break
                elif issubclass(type(img), Exception):
                    self._tile_queue.put(TileStreamingException(None, img))
                    break
                try:
                    tiles, _ = find_grayscale_tiles_in_image(img)
                    self._tile_queue.put(tiles)
                except Exception as e:
                    self._tile_queue.put(TileStreamingException(img, e))
        finally:
            self._tile_queue.put("done", timeout=1)

    def run(self):
        tile_loading_process = mp.Process(target=self._stream_cb_tile_tensors)
        log.info(f"Starting subprocess from {mp.current_process().pid} for {self.video_id}")
        tile_loading_process.start()

        try:
            prev_fen = None
            fen_history = [None] * 10
            frame_num = 0

            while self.running:
                tiles = self._tile_queue.get()
                if type(tiles) == str and tiles == 'done':
                    # video is over
                    break
                frame_num += 1
                sec_into_video = (frame_num - 10) / self.frame_source.fps

                if self._frame_processed_callback is not None:
                    self._frame_processed_callback()

                if tiles is None:
                    log.debug(f"{self.video_id}: No position for frame {frame_num} ({sec_into_video:0.3f}s), skipping")
                    continue
                elif issubclass(type(tiles), Exception):
                    try:
                        raise tiles
                    except TileStreamingException as e:
                        handle_failed_video(e.img, frame_num, sec_into_video, self.video_id)
                    except Exception as e:
                        handle_failed_video(None, frame_num, sec_into_video, self.video_id)
                    continue

                fen = process_tiles(tiles)
                fen_history = fen_history[1:] + [fen]

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
        finally:
            if tile_loading_process.is_alive():
                log.info(f"Terminating child process for vid: {self.video_id}")
                tile_loading_process.terminate()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.frame_source.running = False
