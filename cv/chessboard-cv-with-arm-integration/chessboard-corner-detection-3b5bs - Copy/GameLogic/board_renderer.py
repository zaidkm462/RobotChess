import cv2
import chess
import chess.svg
import cairosvg
import numpy as np


def render_board_image(board, window_name="Board", size=500, orientation=chess.WHITE):
    svg = chess.svg.board(
        board=board,
        orientation=orientation,
        lastmove=board.peek() if board.move_stack else None,
        size=size
    )

    png_bytes = cairosvg.svg2png(bytestring=svg.encode("utf-8"))
    png_array = np.frombuffer(png_bytes, dtype=np.uint8)
    img = cv2.imdecode(png_array, cv2.IMREAD_COLOR)

    cv2.imshow(window_name, img)