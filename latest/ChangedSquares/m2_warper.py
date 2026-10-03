import cv2
import numpy as np

# --- الإعدادات الداخلية للموجيول ---
OUTPUT_SIZE = 800  # حجم الصورة المربعة الناتجة (800x800 بكسل)
GRID_CELLS = 8     # عدد مربعات الشطرنج (8x8)

class ImageWarper:
    def __init__(self):
        # نقاط الهدف: الأركان الأربعة للمربع المثالي الذي نريده
        self.dst_points = np.array([
            [0, 0],
            [OUTPUT_SIZE - 1, 0],
            [OUTPUT_SIZE - 1, OUTPUT_SIZE - 1],
            [0, OUTPUT_SIZE - 1]
        ], dtype="float32")

    def run(self, image, src_points):
        """
        تستقبل الصورة الأصلية والنقاط الأربع، وتعيد:
        1. صورة الرقعة مسطحة (Warped)
        2. صورة الرقعة مع شبكة 8x8 (Grid)
        """
        # --- الجزء الأول: تسطيح المنظور ---
        # حساب مصفوفة التحويل (Transformation Matrix)
        M = cv2.getPerspectiveTransform(src_points, self.dst_points)
        # تنفيذ التحويل
        warped_image = cv2.warpPerspective(image, M, (OUTPUT_SIZE, OUTPUT_SIZE))

        # --- الجزء الثاني: رسم الشبكة ---
        grid_image = warped_image.copy()
        step = OUTPUT_SIZE // GRID_CELLS

        for i in range(1, GRID_CELLS):
            # رسم الخطوط الرأسية
            cv2.line(grid_image, (i * step, 0), (i * step, OUTPUT_SIZE), (0, 255, 0), 2)
            # رسم الخطوط الأفقية
            cv2.line(grid_image, (0, i * step), (OUTPUT_SIZE, i * step), (0, 255, 0), 2)

        return warped_image, grid_image