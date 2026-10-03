import cv2
import numpy as np
import urllib.request

URL = "http://192.168.5.5:8080/photo.jpg"

class Camera:
    def __init__(self):
        pass

    def capture(self):
        """
        تتصل بالرابط، تجلب الصورة، وتحولها إلى مصفوفة قابلة للقراءة عبر OpenCV.
        ترجع الصورة (cv2 image)، أو ترجع None في حال حدوث خطأ.
        """
        try:
            # إرسال طلب HTTP وجلب البيانات
            img_resp = urllib.request.urlopen(URL)

            # قراءة البيانات الخام وتحويلها إلى مصفوفة من بايتات (8-bit)
            imgnp = np.frombuffer(img_resp.read(), dtype=np.uint8)

            # فك تشفير مصفوفة البايتات إلى صورة بـ 3 قنوات ألوان (BGR)
            img = cv2.imdecode(imgnp, cv2.IMREAD_COLOR)

            return img

        except Exception as e:
            # طباعة الخطأ لتسهيل تتبع المشاكل دون إيقاف البرنامج
            print(f"Error fetching frame: {e}")
            return None


