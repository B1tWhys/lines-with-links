import numpy as np
from pytest import approx
import cv2

from video_processing.tensorflow.frame_analyzer import extract_fen
from video_processing.tensorflow.chessboard_finder import findChessboardCorners

from pathlib import Path
from PIL import Image


def assert_test_image_contains_fen(img_name, expected_fen):
    img = load_test_img(img_name)
    assert extract_fen(img) == expected_fen


def load_test_img(img_name):
    img_path = Path(__file__).parent / 'test_images' / (img_name + '.png')
    img = Image.open(img_path)
    return img


def test_position_extraction():
    assert_test_image_contains_fen('gothamchess_1', '2kr3r/ppp2pp1/5n1p/4n1N1/2Pqp1b1/3P2P1/P1PQ1PBP/1RB2RK1')
    assert_test_image_contains_fen('gothamchess_2', '8/1pq2ppk/r1p1nn1p/p1b1p3/P1N1P1BP/2P1B1P1/1P2QPK1/3R4')
    assert_test_image_contains_fen('gothamchess_2', None)
    # assert_test_image_contains_fen('naroditsky_1', 'r1bq1rk1/pp3ppp/2nb1n2/2p5/2B5/3P1N2/PP3PPP/RNBQ1RK1')
    # assert_test_image_contains_fen('agadmator_1', '2q1rb2/pR3pkr/3p2pN/2nPp1QP/1nB1P1b1/6N1/PBP3P1/5RK1')


def assert_find_chessboard_corners_result(img_name: str, expected_corners: np.array):
    # img = cv2.imread("/tmp/foo.jpg")
    pil_img = load_test_img(img_name)
    img = np.asarray(pil_img.convert('L'), dtype=np.uint8)
    detected_corners = findChessboardCorners(img)
    assert np.allclose(detected_corners, expected_corners, atol=3)


def test_find_cb_corners():
    # assert_find_chessboard_corners_result('gothamchess_1', np.array([28, 3, 495, 470]))
    assert_find_chessboard_corners_result('gothamchess_2', np.array([28, 3, 495, 470]))
    # assert_find_chessboard_corners_result('naroditsky_1', np.array([370, 0, 853, 478]))
    # assert_find_chessboard_corners_result('agadmator_1', np.array([88, 70, 476, 455]))
