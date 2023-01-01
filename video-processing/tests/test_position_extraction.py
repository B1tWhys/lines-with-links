from video_processing.tensorflow.frame_analyzer import extract_fen
from pathlib import Path
from PIL import Image

def assert_test_image_contains_fen(img_name, expected_fen):
    img_path = Path(__file__).parent / 'test_images' / (img_name + '.png')
    img = Image.open(img_path)
    assert extract_fen(img) == expected_fen

def test_position_extraction():
    assert_test_image_contains_fen('gothamchess_1', '2kr3r/ppp2pp1/5n1p/4n1N1/2Pqp1b1/3P2P1/P1PQ1PBP/1RB2RK1')
    assert_test_image_contains_fen('gothamchess_2', '8/1pq2ppk/r1p1nn1p/p1b1p3/P1N1P1BP/2P1B1P1/1P2QPK1/3R4')
    assert_test_image_contains_fen('naroditsky_1', 'r1bq1rk1/pp3ppp/2nb1n2/2p5/2B5/3P1N2/PP3PPP/RNBQ1RK1')
