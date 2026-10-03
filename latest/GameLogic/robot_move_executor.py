import chess


class RobotMoveExecutor:
    def __init__(self, arm):
        self.arm = arm

    def execute_move(self, move: chess.Move, board_before: chess.Board):
        if move not in board_before.legal_moves:
            raise ValueError(f"Move is not legal in current board: {move.uci()}")

        if board_before.is_castling(move):
            self._execute_castling(move, board_before)
            return

        if board_before.is_en_passant(move):
            self._execute_en_passant(move, board_before)
            return

        if board_before.is_capture(move):
            self._execute_capture(move)
            return

        self._execute_normal(move)

    def _execute_normal(self, move: chess.Move):
        from_sq = chess.square_name(move.from_square)
        to_sq = chess.square_name(move.to_square)

        self.arm.pick(from_sq)
        self.arm.place(to_sq)
        self.arm.move_to_ref()


    def _execute_capture(self, move: chess.Move):
        from_sq = chess.square_name(move.from_square)
        to_sq = chess.square_name(move.to_square)

        self.arm.pick(to_sq)
        self.arm.throw_piece()
        self.arm.pick(from_sq)
        self.arm.place(to_sq)

    def _execute_en_passant(self, move: chess.Move, board_before: chess.Board):
        from_sq = chess.square_name(move.from_square)
        to_sq = chess.square_name(move.to_square)

        if board_before.turn == chess.WHITE:
            captured_square = move.to_square - 8
        else:
            captured_square = move.to_square + 8

        captured_sq = chess.square_name(captured_square)

        self.arm.pick(captured_sq)
        self.arm.throw_piece()
        self.arm.pick(from_sq)
        self.arm.place(to_sq)

    def _execute_castling(self, move: chess.Move, board_before: chess.Board):
        king_from = chess.square_name(move.from_square)
        king_to = chess.square_name(move.to_square)

        if board_before.turn == chess.WHITE:
            if move.to_square == chess.G1:
                rook_from = "h1"
                rook_to = "f1"
            else:
                rook_from = "a1"
                rook_to = "d1"
        else:
            if move.to_square == chess.G8:
                rook_from = "h8"
                rook_to = "f8"
            else:
                rook_from = "a8"
                rook_to = "d8"

        self.arm.pick(king_from)
        self.arm.place(king_to)
        self.arm.pick(rook_from)
        self.arm.place(rook_to)
