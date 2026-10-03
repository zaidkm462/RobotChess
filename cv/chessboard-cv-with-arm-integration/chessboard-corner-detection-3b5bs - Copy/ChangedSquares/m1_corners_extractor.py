import json
import os
import numpy as np
import supervision as sv
from inference import get_model


API_KEY = os.getenv("ROBOFLOW_API_KEY")
MODEL_ID = "chessboard-detection-yqcnu/3"
CONF_THRESHOLD = 0.005
CORNERS_JSON_PATH = os.path.join(os.path.dirname(__file__), "board_corners.json")


class CornerExtractor:
    def __init__(self):
        # الموديول يقرأ إعداداته من الأعلى مباشرة
        self.model = get_model(model_id=MODEL_ID, api_key=API_KEY)

    def run(self, image):
        file_points = self._load_points_from_json()
        if file_points is not None:
            return file_points

        results = self.model.infer(image, confidence=CONF_THRESHOLD)[0]
        detections = sv.Detections.from_inference(results)

        if len(detections) < 4:
            return None

        # تصفية أعلى 4 ثقة
        top_indices = np.argsort(detections.confidence)[-4:][::-1]
        points = [[(detections.xyxy[i][0] + detections.xyxy[i][2]) / 2,
                   (detections.xyxy[i][1] + detections.xyxy[i][3]) / 2] for i in top_indices]

        return self._order_points(np.array(points, dtype="float32"))

    def _load_points_from_json(self):
        if not os.path.exists(CORNERS_JSON_PATH):
            return None

        try:
            with open(CORNERS_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

        points = data.get("points")
        if not isinstance(points, list) or len(points) != 4:
            return None

        try:
            pts = np.array(points, dtype="float32")
        except (TypeError, ValueError):
            return None

        if pts.shape != (4, 2):
            return None

        return self._order_points(pts)

    def _order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0], rect[2] = pts[np.argmin(s)], pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1], rect[3] = pts[np.argmin(diff)], pts[np.argmax(diff)]
        return rect
