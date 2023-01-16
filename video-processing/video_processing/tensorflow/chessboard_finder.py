from functools import cache

import PIL.Image
import cv2 as cv
import numpy as np
import pandas as pd


def show_img(img):
    cv.imshow('img', img)
    cv.waitKey(500)


@cache
def gen_kernel(n):
    template = np.zeros((n, n), dtype=np.uint8)
    half_n = n // 2
    template[:half_n, :half_n] = 255
    template[half_n:, half_n:] = 255
    return template


def center_of_contour(contour):
    try:
        M = cv.moments(contour)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return np.asarray([cX, cY], dtype=np.float32)
    except ZeroDivisionError:
        return np.mean(contour[:, 0, :], axis=0)


def find_inner_corners(img):
    k_size = 12
    kernel = gen_kernel(k_size)
    match_result = cv.matchTemplate(img, kernel, cv.TM_CCOEFF_NORMED)
    _, match_result = cv.threshold(match_result, .85, 1, cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(match_result.astype(np.uint8), cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    centers = np.array([center_of_contour(c) for c in contours])
    if centers.size < 40:
        return None
    centers += np.array([k_size // 2, k_size // 2])
    return centers


def inner_corners_to_cb_corners(centers, img_h, img_w):
    centers_df = pd.DataFrame(centers, columns=['x', 'y']).round().astype(np.int32)
    value_counts_x = centers_df.x.value_counts()
    value_counts_y = centers_df.y.value_counts()

    columns = value_counts_x[value_counts_x > 2]
    rows = value_counts_y[value_counts_y > 2]

    l_col, r_col = columns.index.to_series().apply(['min', 'max'])
    t_row, b_row = rows.index.to_series().apply(['min', 'max'])

    inner_width = r_col - l_col
    inner_height = b_row - t_row
    square_width = inner_width / 6
    square_height = inner_height / 6
    l_col = max(0, l_col - square_width)
    r_col = min(img_w - 1, r_col + square_width)
    t_row = max(0, t_row - square_height)
    b_row = min(img_h - 1, b_row + square_width)
    return np.array([l_col, t_row], dtype=np.int32), np.array([r_col, b_row], dtype=np.int32)


def findChessboardCorners(img):
    inner_corners = find_inner_corners(img)
    if inner_corners is None:
        return None
    img_h, img_w = img.shape
    corners = inner_corners_to_cb_corners(inner_corners, img_h, img_w)
    return np.concatenate(corners)


def getChessBoardGray(img, corners):
    # img is a grayscale image
    # outer_corners = (x0, y0, x1, y1) for top-left corner to bot-right corner of board
    height, width = img.shape

    # outer_corners could be outside image bounds, pad image as needed
    padl_x = max(0, -corners[0])
    padl_y = max(0, -corners[1])
    padr_x = max(0, corners[2] - width)
    padr_y = max(0, corners[3] - height)

    img_padded = np.pad(img, ((padl_y, padr_y), (padl_x, padr_x)), mode='edge')

    chessboard_img = img_padded[
                     (padl_y + corners[1]):(padl_y + corners[3]),
                     (padl_x + corners[0]):(padl_x + corners[2])]

    # 256x256 px image, 32x32px individual tiles
    # Normalized
    chessboard_img_resized = np.asarray(
        PIL.Image.fromarray(chessboard_img)
        .resize([256, 256], PIL.Image.BILINEAR), dtype=np.uint8) / 255.0
    return chessboard_img_resized


def getChessTilesGray(img, corners):
    chessboard_img_resized = getChessBoardGray(img, corners)
    return getTiles(chessboard_img_resized)


def getTiles(processed_gray_img):
    # Given 256x256 px normalized grayscale image of a chessboard (32x32px per tile)
    # NOTE (values must be in range 0-1)
    # Return a 32x32x64 tile array
    #
    # stack deep 64 tiles
    # so, first slab is tile A1, then A2 etc.
    tiles = np.zeros([32, 32, 64], dtype=np.float32)  # grayscale
    # Assume A1 is bottom left of image, need to reverse rank since images start
    # with origin in top left
    for rank in range(8):  # rows (numbers)
        for file in range(8):  # columns (letters)
            tiles[:, :, (rank * 8 + file)] = \
                processed_gray_img[(7 - rank) * 32:((7 - rank) + 1) * 32, file * 32:(file + 1) * 32]

    return tiles


def find_grayscale_tiles_in_image(img):
    """ Find chessboard and convert into input tiles for CNN """
    if img is None:
        return None, None

    # Convert to grayscale numpy array
    bw_array = np.array(img.convert('L'), dtype=np.uint8)

    # Use computer vision to find orthorectified chessboard outer_corners in image
    corners = findChessboardCorners(bw_array)
    if corners is None:
        return None, None

    # Pull grayscale tiles out given image and chessboard outer_corners
    tiles = getChessTilesGray(bw_array, corners)

    # Return both the tiles as well as chessboard corner locations in the image
    return tiles, corners
