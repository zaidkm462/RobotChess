import json
import time
from pathlib import Path

import serial


class ArduinoArm:
    BASE_INDEX = 0
    SHOULDER_INDEX = 1
    ELBOW_INDEX = 2
    WRIST1_INDEX = 3
    WRIST2_INDEX = 4
    GRIPPER_INDEX = 5

    def __init__(
        self,
        port,
        poses_json_path,
        baudrate=115200,
        open_gripper_angle=35,
        close_gripper_angle=0,
        safe_shoulder_angle=90,
        ref_wait_seconds=1.5,
        target_wait_seconds=1.5,
        shoulder_wait_seconds=2.0,
        gripper_wait_seconds=1.5,
        startup_wait_seconds=2.0,
        timeout=2.0,
        write_timeout=2.0,
    ):
        self.port = port
        self.baudrate = baudrate
        self.poses_json_path = Path(poses_json_path)

        self.open_gripper_angle = int(open_gripper_angle)
        self.close_gripper_angle = int(close_gripper_angle)
        self.safe_shoulder_angle = int(safe_shoulder_angle)

        self.ref_wait_seconds = float(ref_wait_seconds)
        self.target_wait_seconds = float(target_wait_seconds)
        self.shoulder_wait_seconds = float(shoulder_wait_seconds)
        self.gripper_wait_seconds = float(gripper_wait_seconds)
        self.startup_wait_seconds = float(startup_wait_seconds)

        self.timeout = timeout
        self.write_timeout = write_timeout

        self.serial_conn = None
        self.poses = {}

        self.current_main_angles = [90, 90, 90, 90, 90]
        self.current_gripper_angle = 90

        self.load_poses()

    def connect(self):
        if self.serial_conn is not None and self.serial_conn.is_open:
            return

        self.serial_conn = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            write_timeout=self.write_timeout,
        )

        time.sleep(self.startup_wait_seconds)

        try:
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
        except Exception:
            pass

    def disconnect(self):
        if self.serial_conn is not None:
            try:
                if self.serial_conn.is_open:
                    self.serial_conn.close()
            finally:
                self.serial_conn = None

    def load_poses(self):
        if not self.poses_json_path.exists():
            raise FileNotFoundError(f"Poses JSON not found: {self.poses_json_path}")

        with self.poses_json_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, dict) and "poses" in raw and isinstance(raw["poses"], dict):
            raw = raw["poses"]

        if not isinstance(raw, dict):
            raise ValueError("Poses JSON must be an object/dictionary")

        self.poses = raw

    def reload_poses(self):
        self.load_poses()

    def _clamp(self, angle):
        return max(0, min(180, int(angle)))

    def _normalize_main_pose(self, pose, key_name="pose"):
        if pose is None:
            raise ValueError(f"{key_name} is null")

        if not isinstance(pose, (list, tuple)) or len(pose) != 5:
            raise ValueError(f"{key_name} must contain exactly 5 angles")

        return [self._clamp(x) for x in pose]

    def _get_pose(self, key):
        if key in self.poses:
            return self._normalize_main_pose(self.poses[key], key)

        key_lower = key.lower()
        if key_lower in self.poses:
            return self._normalize_main_pose(self.poses[key_lower], key_lower)

        key_upper = key.upper()
        if key_upper in self.poses:
            return self._normalize_main_pose(self.poses[key_upper], key_upper)

        raise KeyError(f"Pose '{key}' not found in JSON")

    def _ensure_connected(self):
        if self.serial_conn is None or not self.serial_conn.is_open:
            raise RuntimeError("Arduino is not connected")

    def _send_line(self, text):
        self._ensure_connected()
        payload = text.encode("utf-8")
        self.serial_conn.write(payload)
        self.serial_conn.flush()

    def send_full_angles(self, full_angles):
        if not isinstance(full_angles, (list, tuple)) or len(full_angles) != 6:
            raise ValueError("full_angles must contain exactly 6 angles")

        final_angles = [self._clamp(x) for x in full_angles]
        cmd = ",".join(str(x) for x in final_angles) + "\n"
        self._send_line(cmd)

        self.current_main_angles = final_angles[:5]
        self.current_gripper_angle = final_angles[5]

    def send_main_angles(self, main_angles):
        final_main = self._normalize_main_pose(main_angles, "main_angles")
        full = final_main + [self._clamp(self.current_gripper_angle)]
        self.send_full_angles(full)

    def set_gripper(self, angle):
        final_angle = self._clamp(angle)
        full = self.current_main_angles[:] + [final_angle]
        self.send_full_angles(full)

    def open_gripper(self):
        self.set_gripper(self.open_gripper_angle)

    def close_gripper(self):
        self.set_gripper(self.close_gripper_angle)

    def go_safe_height(self):
        target_main = self.current_main_angles[:]
        target_main[self.SHOULDER_INDEX] = self.safe_shoulder_angle
        self.send_main_angles(target_main)

    def move_to_ref(self):
        ref_pose = self._get_pose("REF")

        phase1 = self.current_main_angles[:]
        phase1[self.SHOULDER_INDEX] = ref_pose[self.SHOULDER_INDEX]
        self.send_main_angles(phase1)

        time.sleep(self.ref_wait_seconds)

        phase2 = phase1[:]
        phase2[self.BASE_INDEX] = ref_pose[self.BASE_INDEX]
        phase2[self.ELBOW_INDEX] = ref_pose[self.ELBOW_INDEX]
        phase2[self.WRIST1_INDEX] = ref_pose[self.WRIST1_INDEX]
        phase2[self.WRIST2_INDEX] = ref_pose[self.WRIST2_INDEX]
        self.send_main_angles(phase2)

    def _move_to_square_style_pose(self, pose_key):
        target_pose = self._get_pose(pose_key)

        phase1 = target_pose[:]
        phase1[self.SHOULDER_INDEX] = self.current_main_angles[self.SHOULDER_INDEX]
        self.send_main_angles(phase1)

        time.sleep(self.target_wait_seconds)

        phase2 = target_pose[:]
        self.send_main_angles(phase2)

        time.sleep(self.shoulder_wait_seconds)

    def pick(self, square):
        self._move_to_square_style_pose(square)
        self.close_gripper()
        time.sleep(self.gripper_wait_seconds)
        self.go_safe_height()

    def place(self, square):
        self._move_to_square_style_pose(square)
        self.open_gripper()
        time.sleep(self.gripper_wait_seconds)
        self.go_safe_height()

    def throw_piece(self):
        self._move_to_square_style_pose("THROW")
        self.open_gripper()
        time.sleep(self.gripper_wait_seconds)
        self.go_safe_height()
        self.move_to_ref()
