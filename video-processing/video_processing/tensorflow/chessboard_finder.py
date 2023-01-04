from functools import cache

import numpy as np
import PIL.Image
import cv2 as cv


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


def findChessboardCorners(img):
    k_size = 12
    kernel = gen_kernel(k_size)
    match_result = cv.matchTemplate(img, kernel, cv.TM_CCOEFF_NORMED)
    _, match_result = cv.threshold(match_result, .85, 1, cv.THRESH_BINARY)
    nonzero_point_y_coords, nonzero_point_x_coords = np.nonzero(match_result)

    if len(nonzero_point_x_coords) < 30 or len(nonzero_point_y_coords) < 30:
        return None

    show_img(match_result)
    cv.imwrite('./match_result.png', match_result * 255)

    # an offset is necessary to compensate for:
    # * extra pixels get added to the sides of the image when doing the matching step
    # * the coordinates returned are the top left of the kernel (not the center)
    # * the kernel starts matching a pixel before it's completely centered over the pixel
    #
    # after experimenting, 3.5 * the kernel width seems to be about the right offset, although I
    # am admittedly very confused about why that ends up being the right value
    offset = k_size // 2

    left_edge = nonzero_point_x_coords.min() + offset
    right_edge = nonzero_point_x_coords.max() + offset
    top_edge = nonzero_point_y_coords.min() + offset
    bottom_edge = nonzero_point_y_coords.max() + offset

    square_width = (bottom_edge - top_edge) // 6
    square_height = (right_edge - left_edge) // 6

    left_edge -= square_width
    right_edge += square_width
    top_edge -= square_height
    bottom_edge += square_height

    left_edge = max(0, left_edge)
    right_edge = min(img.shape[1], right_edge)
    top_edge = max(0, top_edge)
    bottom_edge = min(img.shape[0], bottom_edge)

    return np.array([left_edge, top_edge, right_edge, bottom_edge], dtype=np.int32)


def getChessTilesColor(img, corners):
    # img is a color RGB image
    # outer_corners = (x0, y0, x1, y1) for top-left corner to bot-right corner of board
    height, width, depth = img.shape
    if depth != 3:
        print("Need RGB color image input")
        return None

    # outer_corners could be outside image bounds, pad image as needed
    padl_x = max(0, -corners[0])
    padl_y = max(0, -corners[1])
    padr_x = max(0, corners[2] - width)
    padr_y = max(0, corners[3] - height)

    img_padded = np.pad(img, ((padl_y, padr_y), (padl_x, padr_x), (0, 0)), mode='edge')

    chessboard_img = img_padded[
                     (padl_y + corners[1]):(padl_y + corners[3]),
                     (padl_x + corners[0]):(padl_x + corners[2]), :]

    # 256x256 px RGB image, 32x32px individual RGB tiles, normalized 0-1 floats
    chessboard_img_resized = np.asarray( \
        PIL.Image.fromarray(chessboard_img) \
            .resize([256, 256], PIL.Image.BILINEAR), dtype=np.float32) / 255.0

    # stack deep 64 tiles with 3 channesl RGB each
    # so, first 3 slabs are RGB for tile A1, then next 3 slabs for tile A2 etc.
    tiles = np.zeros([32, 32, 3 * 64], dtype=np.float32)  # color
    # Assume A1 is bottom left of image, need to reverse rank since images start
    # with origin in top left
    for rank in range(8):  # rows (numbers)
        for file in range(8):  # columns (letters)
            # color
            tiles[:, :, 3 * (rank * 8 + file):3 * (rank * 8 + file + 1)] = \
                chessboard_img_resized[(7 - rank) * 32:((7 - rank) + 1) * 32, file * 32:(file + 1) * 32]

    return tiles


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
    chessboard_img_resized = np.asarray( \
        PIL.Image.fromarray(chessboard_img) \
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


def findGrayscaleTilesInImage(img):
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
