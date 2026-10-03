from skimage.metrics import structural_similarity as ssim
import cv2

# --- الإعدادات الداخلية للموجيول ---
# العتبة التي نعتبر بعدها أن المربع قد تغير فعلاً
SIMILARITY_THRESHOLD = 0.99
CASTLING_SQUARE_SETS = [
    {'e1', 'f1', 'g1', 'h1'},
    {'a1', 'c1', 'd1', 'e1'},
    {'e8', 'f8', 'g8', 'h8'},
    {'a8', 'c8', 'd8', 'e8'},
]


class SSIMDetector:
    def __init__(self):
        pass

    def run(self, dict_before, dict_after):
        """
        تقارن الحالتين وتعود بـ 2 أو 4 مربعات فقط، أو قائمة فارغة.
        """
        scores = {}
        for coord in dict_before.keys():
            img1 = dict_before[coord]
            img2 = dict_after[coord]

            # حساب التشابه
            score, _ = ssim(img1, img2, full=True)
            scores[coord] = score

        # 1. ترتيب كل المربعات من الأكثر تغييراً (الأقل تشابهاً)
        sorted_changes = sorted(scores.items(), key=lambda x: x[1])

        # 2. تصفية المربعات التي تجاوزت العتبة (تغيرت بشكل ملحوظ)
        significant = [item for item in sorted_changes if item[1] < SIMILARITY_THRESHOLD]

        # 3. منطق القرار (Decision Logic)
        if len(significant) >= 4:
            top_four_coords = [significant[i][0] for i in range(4)]
            if set(top_four_coords) in CASTLING_SQUARE_SETS:
                # حالة تبييت (Castling) أو حركة معقدة: نأخذ أول 4
                return top_four_coords
            return [significant[0][0], significant[1][0]]
        elif len(significant) >= 2:
            # نقلة عادية أو أكل قطعة: نأخذ أول 2
            return [significant[0][0], significant[1][0]]

        # في حال لم يحدث تغيير كافٍ
        return []
