import chess


def visual_changed_squares_for_move(board: chess.Board, move: chess.Move) -> set[str]:
    """
    ترجع المربعات التي ستتغير بصريًا إذا طُبقت هذه النقلة على البورد الحالي.
    هذا يشمل:
    - النقلة العادية
    - الأكل
    - التبييت
    - en passant
    - promotion
    """
    before_map = board.piece_map()

    after_board = board.copy(stack=False)
    after_board.push(move)
    after_map = after_board.piece_map()

    changed = set()
    all_squares = set(before_map.keys()) | set(after_map.keys())

    for sq in all_squares:
        if before_map.get(sq) != after_map.get(sq):
            changed.add(chess.square_name(sq))

    return changed


class GameObserver:
    def __init__(self, human_is_white=True, start_fen=None):
        self.board = chess.Board(start_fen) if start_fen else chess.Board()
        self.human_is_white = human_is_white

    def current_actor(self) -> str:
        """
        يحدد هل الدور الحالي للإنسان أم للروبوت.
        """
        if self.board.turn == chess.WHITE:
            return "human" if self.human_is_white else "robot"
        else:
            return "robot" if self.human_is_white else "human"

    def infer_move_from_changed_squares(self, changed_squares: list[str]):
        """
        يأخذ changed_squares من طبقة الرؤية ويحاول إيجاد نقلة قانونية تطابقها.
        """
        observed = set(changed_squares)

        exact_matches = []
        ranked = []

        for move in self.board.legal_moves:
            expected = visual_changed_squares_for_move(self.board, move)
            diff = len(expected ^ observed)  # symmetric difference
            ranked.append((diff, move, expected))

            if expected == observed:
                exact_matches.append((move, expected))

        if len(exact_matches) == 1:
            move, expected = exact_matches[0]
            return {
                "status": "ok",
                "mode": "exact",
                "move": move,
                "expected_squares": sorted(expected),
            }

        if len(exact_matches) > 1:
            return {
                "status": "ambiguous",
                "reason": "more_than_one_legal_move_matches_exactly",
                "candidates": [m.uci() for m, _ in exact_matches],
            }

        ranked.sort(key=lambda x: x[0])

        if not ranked:
            return {
                "status": "illegal",
                "reason": "no_legal_moves_available"
            }

        best_diff, best_move, best_expected = ranked[0]
        second_diff = ranked[1][0] if len(ranked) > 1 else 999

        # سماح خفيف لو SSIM أعطى مربع زائد/ناقص واحد
        if best_diff <= 1 and best_diff < second_diff:
            return {
                "status": "ok",
                "mode": "relaxed",
                "move": best_move,
                "expected_squares": sorted(best_expected),
            }

        return {
            "status": "illegal",
            "reason": "no_legal_move_matches_changed_squares",
            "best_candidate": best_move.uci(),
            "best_candidate_expected_squares": sorted(best_expected),
            "observed_squares": sorted(observed),
            "best_diff": best_diff,
        }

    def observe_changed_squares(self, changed_squares: list[str]):
        result = self.infer_move_from_changed_squares(changed_squares)

        if result["status"] != "ok":
            return result

        move = result["move"]
        san = self.board.san(move)
        uci = move.uci()
        actor_before = self.current_actor()

        self.board.push(move)

        game_over = self.board.is_game_over()
        outcome = self.board.outcome()

        return {
            "status": "applied",
            "uci": uci,
            "san": san,
            "mode": result["mode"],
            "actor_who_moved": actor_before,
            "next_actor": None if game_over else self.current_actor(),
            "fen_after": self.board.fen(),
            "changed_squares_observed": sorted(changed_squares),
            "changed_squares_expected": result["expected_squares"],
            "is_check": self.board.is_check(),
            "is_checkmate": self.board.is_checkmate(),
            "is_stalemate": self.board.is_stalemate(),
            "is_game_over": game_over,
            "outcome": str(outcome) if outcome else None,
        }