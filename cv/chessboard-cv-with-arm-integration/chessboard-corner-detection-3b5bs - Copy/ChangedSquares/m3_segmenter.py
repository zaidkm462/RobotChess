import cv2

# --- الإعدادات الداخلية للموجيول ---
GRID_SIZE = 8
SQUARE_DIM = 90
CENTER_CROP_RATIO = 0.7
BLUR_KERNEL_SIZE = (1, 1)


class BoardSegmenter:
    def __init__(self):
        self.columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.rows = ['8', '7', '6', '5', '4', '3', '2', '1']

    def run(self, warped_image):
        """
        تستقبل الرقعة المسطحة.
        1. تحولها لرمادي.
        2. تطبق Gaussian Blur خفيف لتخفيف الضجيج البصري.
        3. تقسمها لـ 64 مربعاً.
        """
        # 1. التحويل للرمادي
        gray_board = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)

        # 2. تطبيق Gaussian Blur خفيف
        processed_board = cv2.GaussianBlur(gray_board, BLUR_KERNEL_SIZE, 0)

        h, w = processed_board.shape[:2]
        sq_h, sq_w = h // GRID_SIZE, w // GRID_SIZE

        squares_dict = {}

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                y1, y2 = r * sq_h, (r + 1) * sq_h
                x1, x2 = c * sq_w, (c + 1) * sq_w

                square = processed_board[y1:y2, x1:x2]

                crop_h = max(1, int(square.shape[0] * CENTER_CROP_RATIO))
                crop_w = max(1, int(square.shape[1] * CENTER_CROP_RATIO))
                start_y = max(0, (square.shape[0] - crop_h) // 2)
                start_x = max(0, (square.shape[1] - crop_w) // 2)
                end_y = start_y + crop_h
                end_x = start_x + crop_w
                square = square[start_y:end_y, start_x:end_x]

                square_resized = cv2.resize(square, (SQUARE_DIM, SQUARE_DIM))

                coord = self.columns[c] + self.rows[r]
                squares_dict[coord] = square_resized

        return squares_dict
