import os
from queue import Queue
from .helper_functions import predictSideFromFEN, unflipFEN, shortenFEN

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'  # Ignore Tensorflow INFO debug messages
import tensorflow as tf
import numpy as np
from importlib import resources
import logging
from . import chessboard_finder
from dataclasses import dataclass
from PIL import Image

log = logging.getLogger(__name__)

log.info("Initializing tensorflow session")
# Load and parse the protobuf file to retrieve the unserialized graph_def.
with resources.open_binary('video_processing.tensorflow.saved_models', 'frozen_graph.pb') as f:
    graph_def = tf.compat.v1.GraphDef()
    graph_def.ParseFromString(f.read())

# Import graph def and return.
with tf.Graph().as_default() as graph:
    # Prefix every op/nodes in the graph.
    tf.import_graph_def(graph_def, name="tcb")

_tf_session = tf.compat.v1.Session(graph=graph)
x = graph.get_tensor_by_name('tcb/Input:0')
_keep_prob_layer = graph.get_tensor_by_name('tcb/KeepProb:0')
_prediction_layer = graph.get_tensor_by_name('tcb/prediction:0')
probabilities = graph.get_tensor_by_name('tcb/probabilities:0')

log.info("tensorflow initialized")


@dataclass
class Frame:
    vid_id: str
    img: Image.Image
    sec_into_video: float


@dataclass
class FenExtractionResult:
    vid_id: str
    sec_into_video: float
    fen: str

    def __repr__(self):
        return f"vid_id: {self.vid_id}, sec_into_video: {self.sec_into_video:0.3f}, fen: {self.fen}"


def frame_analysis_worker(inputFrameQueue: Queue, outputFenQueue: Queue):
    log.info("Starting frame analysis worker")
    while True:
        frame: Frame = inputFrameQueue.get()
        if frame is None:
            break
        fen = extract_fen(frame.img)
        if fen is not None:
            result = FenExtractionResult(frame.vid_id, frame.sec_into_video, fen)
            outputFenQueue.put(result)


def extract_fen(img: Image.Image) -> str | None:
    # Look for chessboard in image, get corners and split chessboard into tiles
    tiles, _ = chessboard_finder.findGrayscaleTilesInImage(img)

    # Exit on failure to find chessboard in image
    if tiles is None:
        log.debug("Couldn't find chessboard in image")
        return None

    # Make prediction on input tiles. Resulting fen *may* be flipped along y-axis
    fen = process_tiles(tiles)

    if fen is None:
        return None
    side = predictSideFromFEN(fen)
    if side == 'b':
        fen = unflipFEN(fen)
    return shortenFEN(fen)


def process_tiles(tiles):
    """Run trained neural network on tiles generated from image"""
    if tiles is None or len(tiles) == 0:
        print("Couldn't parse chessboard")
        return None, 0.0

    # Reshape into Nx1024 rows of input data, format used by neural network
    validation_set = np.swapaxes(np.reshape(tiles, [32 * 32, 64]), 0, 1)

    # Run neural network on data
    guess_prob, guessed = _tf_session.run(
        [probabilities, _prediction_layer],
        feed_dict={x: validation_set, _keep_prob_layer: 1.0})

    # Convert guess into FEN string
    # guessed is tiles A1-H8 rank-order, so to make a FEN we just need to flip the files from 1-8 to 8-1
    label_index_2_name = lambda label_index: ' KQRBNPkqrbnp'[label_index]
    piece_names = list(map(lambda k: '1' if k == 0 else label_index_2_name(k), guessed))  # exchange ' ' for '1' for FEN
    fen = '/'.join([''.join(piece_names[i * 8:(i + 1) * 8]) for i in reversed(range(8))])
    return fen
