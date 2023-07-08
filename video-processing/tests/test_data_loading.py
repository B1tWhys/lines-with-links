from PIL import Image

from video_processing.data_loading import YoutubeFrameSource


class TestYoutubeVideoLoading:
    def test_load_frames(self):
        test_video = "https://www.youtube.com/watch?v=k4T6TJGOSA0"
        frame_source = YoutubeFrameSource(test_video)

        frame_source.stream_frames(stop_after_frames=1)
        first_frame: Image.Image = frame_source.img_output_queue.get(timeout=3)
        assert first_frame.height == 480
        assert first_frame.width == 854
        assert frame_source.fps == 30
        assert frame_source.video_id == "k4T6TJGOSA0"
