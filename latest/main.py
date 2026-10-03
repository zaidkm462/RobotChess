import time

import cv2

from ChangedSquares.changed_squares import get_changed_squares
from GameLogic.game_observer import GameObserver
from GameLogic.board_renderer import render_board_image
from GameLogic.game_controller import GameController
from Engine.engine import Engine
from Interfacing.camera import Camera
from Interfacing.arduino_arm import ArduinoArm
from GameLogic.robot_move_executor import RobotMoveExecutor

ref_frame = None

ARM_ENABLED = True
ARM_PORT = "COM11"
ARM_POSES_JSON = "robot_arm_poses.json"

observer = GameObserver(human_is_white=True)
engine = Engine(use_fake=True, stockfish_path='C:\\Users\\Alarabi karbala\\Desktop\\p2\\latest\\stockfish\\stockfish-windows-x86-64-avx2.exe')

arm = None
robot_move_executor = None

if ARM_ENABLED:
    try:
        arm = ArduinoArm(
            port=ARM_PORT,
            poses_json_path=ARM_POSES_JSON,
        )
        arm.connect()
        arm.open_gripper()
        arm.move_to_ref()
        time.sleep(1)
        robot_move_executor = RobotMoveExecutor(arm)
    except Exception as e:
        print("Arduino arm init failed:", e)
        arm = None
        robot_move_executor = None

controller = GameController(observer, engine, render_board_image, robot_move_executor=robot_move_executor)
camera = Camera()


def sync_turn_indicator():
    if arm is None:
        return

    try:
        if controller.state == controller.WAITING_HUMAN_MOVE:
            arm.clear_pending_input()
            arm.led_human_turn()
        else:
            arm.clear_pending_input()
            arm.led_robot_turn()
    except Exception as e:
        print("Turn indicator sync failed:", e)


def new_frame(frame):
    global ref_frame

    if ref_frame is None:
        ref_frame = frame.copy()
        sync_turn_indicator()
        return

    changed_squares = get_changed_squares(ref_frame, frame)
    print(f"Changed squares: {changed_squares}")

    accepted = controller.handle_external_move(changed_squares)
    sync_turn_indicator()
    if accepted:
        ref_frame = frame.copy()


def wait_for_next_capture_trigger():
    if arm is None:
        while True:
            key = cv2.waitKey(0) & 0xFF
            if key == 27:
                return False
            if key == 13:
                return True

    while True:
        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            return False

        try:
            if arm.wait_for_button_press(timeout=0.05, poll_interval=0.01):
                print("Arduino button pressed")
                return True
        except Exception as e:
            print("Button read failed:", e)
            return False


def main():
    frames = ["1.jpeg", "2.jpeg", "3.jpeg", "4.jpeg", "5.jpeg", "6.jpeg", "7.jpeg", "8.jpeg"]

    i = 0

    if arm is not None:
        print("Push button = next incoming move")
    else:
        print("Enter = next incoming move")
    print("ESC   = quit")

    controller.show_board()
    new_frame(camera.capture())

    while True:
        triggered = wait_for_next_capture_trigger()
        if not triggered:
            break
        new_frame(camera.capture())

    engine.quit()

    if arm is not None:
        arm.disconnect()

    cv2.destroyAllWindows()


def main2():
    frames = ["buff/1.jpg", "buff/2.jpg"]

    i = 0

    print("Enter = next incoming move")
    print("ESC   = quit")

    controller.show_board()
    new_frame(cv2.imread(frames[i]))
    i += 1

    while True:
        key = cv2.waitKey(0) & 0xFF
        if key == 27: break # ESC
        if key == 13:
            new_frame(cv2.imread(frames[i]))
            i += 1

    engine.quit()

    if arm is not None:
        arm.disconnect()

    cv2.destroyAllWindows()



def handle_next_data_move(data_moves, index):
    if index >= len(data_moves):
        print("لا توجد حركات أخرى.")
        return index

    incoming_move = list(data_moves[index])
    print(f"\n[{index}] Incoming move from data source: {incoming_move}")

    accepted = controller.handle_external_move(incoming_move)
    sync_turn_indicator()

    if accepted:
        print("Move processed.")
    else:
        print("Move rejected or waiting for correction.")

    return index + 1

if __name__ == "__main__":
    main()
