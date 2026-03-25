import time
import re
import csv
import os
import numpy as np
import cv2
from mss import mss
import pytesseract

# 🔥 SET TESSERACT PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print("🚀 Aviator Scraper Started...")
print("📡 Monitoring game...")

# 🔥 SET YOUR REGIONS (adjusted by you)
 
multiplier_region = {"top": 500, "left": 1277, "width": 416, "height": 100}
fly_region = {"top": 466, "left": 1277, "width": 291, "height": 50}

# --- Resume last saved value ---
last_saved = ""
if os.path.exists('aviator.csv'):
    with open('aviator.csv', 'r') as f:
        lines = f.readlines()
        if lines:
            last_saved = lines[-1].strip().split(',')[1]
            print("🔁 Resuming from last value:", last_saved)

flew_detected = False
counter = 0

with mss() as sct:
    while True:
        counter += 1

        # ⏳ Heartbeat
        if counter % 6 == 0:
            print("⏳ Running...", time.strftime("%H:%M:%S"))

        # --- DETECT FLEW AWAY ---
        fly_img = np.array(sct.grab(fly_region))
        gray = cv2.cvtColor(fly_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

        fly_text = pytesseract.image_to_string(thresh)

        if "FLEW" in fly_text.upper():
            if not flew_detected:
                print("🚀 ROUND ENDED")
                flew_detected = True

                # 🔥 wait longer for stability
                time.sleep(0.5)

                # --- RETRY OCR (3 attempts) ---
                val = None

                val = None

                for attempt in range(3):
                    mult_img = np.array(sct.grab(multiplier_region))

                    # --- CONVERT TO HSV ---
                    hsv = cv2.cvtColor(mult_img, cv2.COLOR_BGR2HSV)

                    # --- RED COLOR MASK ---
                    lower_red1 = np.array([0, 120, 120])
                    upper_red1 = np.array([10, 255, 255])

                    lower_red2 = np.array([170, 120, 120])
                    upper_red2 = np.array([180, 255, 255])

                    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

                    mask = mask1 + mask2

                    # apply mask
                    result = cv2.bitwise_and(mult_img, mult_img, mask=mask)

                    # convert to grayscale
                    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

                    # enlarge
                    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

                    # threshold
                    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

                    # blur
                    thresh = cv2.GaussianBlur(thresh, (3,3), 0)

                    # OCR
                    mult_text = pytesseract.image_to_string(
                        thresh,
                        config='--psm 7 -c tessedit_char_whitelist=0123456789.x'
                    )

                    print(f"🔍 Attempt {attempt+1}:", mult_text)

                    match = re.findall(r'\d+\.\d+x', mult_text)

                    if match:
                        val = match[0]
                        break

                    time.sleep(0.2)

                # --- SAVE RESULT ---
                if val and val != last_saved:
                    last_saved = val

                    with open('25march.csv', 'a', buffering=1, newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), val])

                    print("✅ Saved:", val)

                else:
                    print("⚠️ OCR failed or duplicate")

        else:
            flew_detected = False

        time.sleep(0.3)