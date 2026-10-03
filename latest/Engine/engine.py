import chess
import chess.engine


class Engine:
    def __init__(self, stockfish_path=None, use_fake=True):
        self.stockfish_path = stockfish_path
        self.use_fake = use_fake
        self.index = 0
        self.real_engine = None

        # الحركات الملقنة داخل المحرك نفسه
        self.scripted_moves = [
            "b7b6",
            "c7c6",
            "b6b5",
        ]

        if not self.use_fake and self.stockfish_path is not None:
            self.real_engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)

    def fake(
        self,
        board,
        limit,
        *,
        game=None,
        info=None,
        ponder=False,
        draw_offered=False,
        root_moves=None,
        options={},
        opponent=None,
    ):
        if self.index >= len(self.scripted_moves):
            return None

        move_text = self.scripted_moves[self.index]

        try:
            move = board.parse_uci(move_text)
        except ValueError:
            move = board.parse_san(move_text)

        if move not in board.legal_moves:
            raise ValueError(f"Illegal scripted move: {move_text}")

        self.index += 1
        return move

    def play(
        self,
        board,
        limit,
        *,
        game=None,
        info=None,
        ponder=False,
        draw_offered=False,
        root_moves=None,
        options={},
        opponent=None,
    ):
        if self.use_fake:
            return self.fake(
                board,
                limit,
                game=game,
                info=info,
                ponder=ponder,
                draw_offered=draw_offered,
                root_moves=root_moves,
                options=options,
                opponent=opponent,
            )

        if self.real_engine is None:
            raise ValueError("Real engine is not initialized")

        result = self.real_engine.play(
            board,
            limit,
            game=game,
            info=info,
            ponder=ponder,
            draw_offered=draw_offered,
            root_moves=root_moves,
            options=options,
            opponent=opponent,
        )

        return result.move

    def quit(self):
        if self.real_engine is not None:
            self.real_engine.quit()