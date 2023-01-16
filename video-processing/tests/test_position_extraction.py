from pathlib import Path

import numpy as np
from PIL import Image

from video_processing.tensorflow.chessboard_finder import findChessboardCorners
from video_processing.tensorflow.frame_analyzer import extract_fen


def assert_test_image_contains_fen(img_name, expected_fen):
    img = load_test_img(img_name)
    assert extract_fen(img) == expected_fen


def load_test_img(img_name):
    img_path = Path(__file__).parent / 'test_images' / (img_name + '.png')
    img = Image.open(img_path)
    return img


def test_position_extraction():
    assert_test_image_contains_fen('gothamchess_1', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
    assert_test_image_contains_fen('gothamchess_2', 'rnbq3r/ppp1pkb1/6p1/2PP2Pp/2B2BnP/2N2Q2/PP3P2/R3K2R')
    assert_test_image_contains_fen('gothamchess_3', None)
    assert_test_image_contains_fen('naroditsky_1', 'r1bq1rk1/pp3ppp/2nb1n2/2p5/2B5/3P1N2/PP3PPP/RNBQ1RK1')
    # assert_test_image_contains_fen('agadmator_1', '2q1rb2/pR3pkr/3p2pN/2nPp1QP/1nB1P1b1/6N1/PBP3P1/5RK1')


def assert_find_chessboard_corners_result(img_name: str, expected_corners: np.array):
    pil_img = load_test_img(img_name)
    img = np.asarray(pil_img.convert('L'), dtype=np.uint8)
    detected_corners = findChessboardCorners(img)
    assert np.allclose(detected_corners, expected_corners, atol=3)


def test_find_cb_corners():
    assert_find_chessboard_corners_result('gothamchess_1', np.array([28, 3, 495, 470]))
    assert_find_chessboard_corners_result('gothamchess_2', np.array([28, 3, 495, 470]))
    assert_find_chessboard_corners_result('naroditsky_1', np.array([370, 0, 853, 478]))
    assert_find_chessboard_corners_result('agadmator_1', np.array([88, 70, 476, 455]))
