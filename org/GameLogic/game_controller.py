import chess
import chess.engine
import os


class GameController:
    WAITING_HUMAN_MOVE = "WAITING_HUMAN_MOVE"
    WAITING_ROBOT_CONFIRMATION = "WAITING_ROBOT_CONFIRMATION"
    GAME_OVER = "GAME_OVER"

    def __init__(self, observer, engine, renderer, robot_move_executor=None):
        self.observer = observer
        self.engine = engine
        self.renderer = renderer
        self.robot_move_executor = robot_move_executor

        self.state = self.WAITING_HUMAN_MOVE
        self.expected_robot_move = None

        self.orientation = chess.WHITE if observer.human_is_white else chess.BLACK

    def show_board(self):
        self.renderer(self.observer.board, orientation=self.orientation)

    def _set_human_turn_indicator(self):
        if self.robot_move_executor is None:
            return

        arm = getattr(self.robot_move_executor, "arm", None)
        if arm is None:
            return

        try:
            arm.clear_pending_input()
            arm.led_human_turn()
        except Exception:
            pass

    def _set_robot_turn_indicator(self):
        if self.robot_move_executor is None:
            return

        arm = getattr(self.robot_move_executor, "arm", None)
        if arm is None:
            return

        try:
            arm.clear_pending_input()
            arm.led_robot_turn()
        except Exception:
            pass

    def print_expected_robot_move(self):
        if self.expected_robot_move is None:
            print("Expected robot move: None")
        else:
            print("Expected robot move:", self.expected_robot_move.uci())

    def finish_if_game_over(self):
        if self.observer.board.is_game_over():
            self.state = self.GAME_OVER
            self.expected_robot_move = None
            print("Game Over:", self.observer.board.outcome())
            return True
        return False

    def handle_external_move(self, changed_squares):
        changed_squares = list(changed_squares)

        if self.state == self.GAME_OVER:
            print("Game is already over.")
            return False

        if self.state == self.WAITING_HUMAN_MOVE:
            return self._handle_human_move(changed_squares)

        if self.state == self.WAITING_ROBOT_CONFIRMATION:
            return self._handle_robot_move(changed_squares)

        print("Unknown state:", self.state)
        return False

    def _handle_human_move(self, changed_squares):
        self._set_robot_turn_indicator()
        result = self.observer.observe_changed_squares(changed_squares)

        if result["status"] != "applied":
            print("Human move rejected:", result)
            return False

        print("Human move accepted:", result["uci"], f"({result['san']})")
        self.show_board()

        if self.finish_if_game_over():
            return True

        robot_move = self.engine.play(
            self.observer.board,
            chess.engine.Limit(time=0.1)
        )

        if robot_move is None:
            raise ValueError("Engine returned no move while game is not over")

        self.expected_robot_move = robot_move
        self.state = self.WAITING_ROBOT_CONFIRMATION
        self.print_expected_robot_move()

        if self.robot_move_executor is not None:
            try:
                board_before_robot_move = self.observer.board.copy(stack=False)
                self.robot_move_executor.execute_move(robot_move, board_before_robot_move)
            except Exception as e:
                print("Robot physical move failed:", e)

        return True

    def _handle_robot_move(self, changed_squares):
        if self.expected_robot_move is None:
            print("Error: no expected robot move stored")
            return False

        preview = self.observer.infer_move_from_changed_squares(changed_squares)

        if preview["status"] != "ok":
            print("Robot move rejected before apply:", preview)
            return False

        detected_move = preview["move"]

        if detected_move != self.expected_robot_move:
            print("Robot move mismatch")
            print("Detected :", detected_move.uci())
            print("Expected :", self.expected_robot_move.uci())
            return False

        result = self.observer.observe_changed_squares(changed_squares)

        if result["status"] != "applied":
            print("Robot move could not be applied:", result)
            return False

        print("Robot move confirmed:", result["uci"], f"({result['san']})")

        self.expected_robot_move = None
        self.state = self.WAITING_HUMAN_MOVE
        self._set_human_turn_indicator()

        self.show_board()
        self.finish_if_game_over()

        return True