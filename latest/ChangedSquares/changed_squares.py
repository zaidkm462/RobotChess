import cv2
import numpy as np
import os
from ChangedSquares.m1_corners_extractor import CornerExtractor
from ChangedSquares.m2_warper import ImageWarper
from ChangedSquares.m3_segmenter import BoardSegmenter
from ChangedSquares.m4_ssim import SSIMDetector



# --- 1. دالة المعالجة الصرفة (Processing Only) ---

def run_full_pipeline(extractor, warper, segmenter, frame, reference_points=None):
    """تنفذ الخطوات الحسابية فقط وتعيد البيانات الخام"""
    points = reference_points if reference_points is not None else extractor.run(frame)

    if points is None:
        return None, None, None, None

    warped, grid = warper.run(frame, points)
    squares_dict = segmenter.run(warped)

    return squares_dict, points, warped, grid


# --- 2. دالة العرض المرئي (Visualization Only) ---

def visualize_stage_results(frame, points, warped, grid, squares_dict, label="frame"):
    """
    تأخذ المخرجات الخام وتقوم برسمها وتجميعها وحفظها للعرض.
    label: نص لتمييز الملفات (مثلاً 'before' أو 'after')
    """
    # أ. رسم النقاط على الصورة الأصلية
    img_corners = frame.copy()
    for i, pt in enumerate(points):
        cv2.circle(img_corners, (int(pt[0]), int(pt[1])), 10, (0, 255, 0), -1)
        cv2.putText(img_corners, str(i + 1), (int(pt[0]) + 10, int(pt[1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # ب. تجميع الـ Contact Sheet (64 مربع)
    margin, sq_size = 5, 90
    canvas_size = (sq_size * 8) + (margin * 9)
    contact_sheet = np.zeros((canvas_size, canvas_size), dtype=np.uint8)

    columns, rows = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'], ['8', '7', '6', '5', '4', '3', '2', '1']

    for r_idx, r_lab in enumerate(rows):
        for c_idx, c_lab in enumerate(columns):
            square_img = squares_dict[c_lab + r_lab]
            y_off = margin + r_idx * (sq_size + margin)
            x_off = margin + c_idx * (sq_size + margin)
            contact_sheet[y_off:y_off + sq_size, x_off:x_off + sq_size] = square_img

    # ج. حفظ الملفات بأسماء مميزة
    f1, f2, f3 = f"{label}_1_corners.jpg", f"{label}_2_grid.jpg", f"{label}_3_sheet.jpg"
    cv2.imwrite(f1, img_corners)
    cv2.imwrite(f2, grid)
    cv2.imwrite(f3, contact_sheet)

    # د. الفتح في عارض النظام
    os.startfile(f1)
    os.startfile(f2)
    os.startfile(f3)


def visualize_move_highlight(warped_after, move_coords):
    """
    تأخذ الصورة المسطحة وقائمة بأعلى إحداثيات (مثلاً ['e2', 'e4'])
    وترسم فوقها مستطيلات خضراء شفافة.
    """
    output = warped_after.copy()
    overlay = warped_after.copy()

    sq_size = warped_after.shape[0] // 8
    cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    rows = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7}

    for coord in move_coords:
        c, r = coord[0], coord[1]
        x1 = cols[c] * sq_size
        y1 = rows[r] * sq_size
        x2 = x1 + sq_size
        y2 = y1 + sq_size

        # رسم مستطيل أخضر فاقع على الطبقة العلوية
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)

    # دمج الطبقتين بنسبة شفافية 40% (0.4)
    alpha = 0.4
    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

    cv2.imwrite("res_4_detected_move.jpg", output)
    os.startfile("res_4_detected_move.jpg")

# --- 3. الدالة الرئيسية (The Orchestrator) ---

_EXTRACTOR = CornerExtractor()
_WARPER = ImageWarper()
_SEGMENTER = BoardSegmenter()
_DETECTOR = SSIMDetector()


def get_changed_squares(img1, img2):

    # معالجة الصورة الأولى (Before)
    img_before = img1
    #img_before = cv2.rotate(img_before, cv2.ROTATE_180)

    print("📸 Processing 'Before' Frame...")
    sq_before, pts_ref, warp_before, grid_before = run_full_pipeline(_EXTRACTOR, _WARPER, _SEGMENTER, img_before)

    if sq_before is None: return print("ERROR processing img1")

    # استدعاء دالة العرض المنفصلة للقطة الأولى
    visualize_stage_results(img_before, pts_ref, warp_before, grid_before, sq_before, "before")

    # معالجة الصورة الثانية (After) باستخدام نفس النقاط
    img_after = img2
    #img_after = cv2.rotate(img_after, cv2.ROTATE_180)

    print("📸 Processing 'After' Frame...")
    sq_after, pts_ref2, warp_after, grid_after = run_full_pipeline(
        _EXTRACTOR, _WARPER, _SEGMENTER, img_after, reference_points=pts_ref
    )

    if sq_after is None: return print("ERROR processing img2")
    # استدعاء دالة العرض للقطة الثانية
    visualize_stage_results(img_after, pts_ref, warp_after, grid_after, sq_after, "after")

    print("🔍 Analyzing differences...")
    detected_coords = _DETECTOR.run(sq_before, sq_after)

    if detected_coords:
        count = len(detected_coords)
        print(f"🚨 {count} Squares Detected: {detected_coords}")

        # استدعاء دالة التلوين (التي برمجناها سابقاً)
        visualize_move_highlight(warp_after, detected_coords)
    else:
        return print("✅ No significant move detected.")

    return detected_coords


