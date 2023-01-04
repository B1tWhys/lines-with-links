#!/bin/bash -e

python -m cProfile -o find-cb.prof /home/skyler/.cache/pypoetry/virtualenvs/video-processing-cjBJpIv2-py3.10/bin/pytest -k test_position_extraction_performance
gprof2dot -f pstats -z chessboard_finder:307:findGrayscaleTilesInImage find-cb.prof | dot -Tpng -o find-cb.prof.png
