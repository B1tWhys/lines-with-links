import timeit

from video_processing.db import init_sqlite_db
from video_processing.tensorflow.frame_analyzer import extract_fen
from pathlib import Path
from PIL import Image
from video_processing.data_loading import FrameSource
from video_processing.video_processing_task import VideoProcessingTask
from video_processing.tensorflow.chessboard_finder import findGrayscaleTilesInImage


class FileFrameSource(FrameSource):
    file_path: str

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def __len__(self):
        return 1000

    @property
    def _source(self) -> str:
        return self.file_path

    @property
    def fps(self) -> float:
        return 30

    @property
    def video_id(self) -> str:
        return "testvideo"


def test_performance():
    init_sqlite_db()
    vid_path = Path(__file__).parent / 'test_images' / "test_video_1.mp4"
    frame_source = FileFrameSource('/tmp/test_video.mp4')
    task = VideoProcessingTask(frame_source)
    task.run()

    # queue = frame_source.img_output_queue
    # thread = Thread(target=frame_source.stream_frames)
    # thread.start()
    # print(timeit.Timer(lambda: queue.get()).timeit(5000) / 5000)
    # frame_source.running = False
    # thread.join()
    # assert 1 == 2

def assert_test_image_contains_fen(img_name, expected_fen):
    img_path = Path(__file__).parent / 'test_images' / (img_name + '.png')
    img = Image.open(img_path)
    assert extract_fen(img) == expected_fen

# python -m cProfile -o find-cb.prof /home/skyler/.cache/pypoetry/virtualenvs/video-processing-cjBJpIv2-py3.10/bin/pytest -k test_position_extraction_performance; gprof2dot -f pstats find-cb.prof | dot -Tpng -o find-cb.prof.png
def test_position_extraction_performance():
    img_path = Path(__file__).parent / 'test_images' / 'agadmator_1.png'
    img = Image.open(img_path)

    # original = 0.01471
    # c60a6dc  = 0.01094
    # 8fd8504  =
    timeit_result = timeit.Timer(lambda: findGrayscaleTilesInImage(img)).timeit(1000)
    print(f"timeit result: {timeit_result / 1000}")


# def test_position_extraction_performance():
#     img_path = Path(__file__).parent / 'test_images' / 'agadmator_1.png'
#     img = Image.open(img_path)
#
#     findGrayscaleTilesInImage(img)
