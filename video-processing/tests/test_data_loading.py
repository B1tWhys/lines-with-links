from video_processing.data_loading import YoutubeFrameSource
from PIL import Image


class TestYoutubeVideoLoading:
    def test_load_frames(self):
        test_video = "https://www.youtube.com/watch?v=k4T6TJGOSA0"
        frame_source = YoutubeFrameSource(test_video)
        stream = frame_source.stream_frames()
        first_frame: Image.Image = next(stream)
        assert first_frame.height == 480
        assert first_frame.width == 854
        assert frame_source.fps == 30
