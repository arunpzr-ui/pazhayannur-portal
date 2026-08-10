import os
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageEnhance

SRC_DIR = "D:/pazhayannur.com/src/assets/administration/members"
TARGET_W, TARGET_H = 720, 960  # 3:4 portrait, matches the card's aspect-[3/4]

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def detect_face_box(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.08, minNeighbors=5, minSize=(60, 60)
    )
    if len(faces) == 0:
        return None
    # pick the largest detected face
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    return faces[0]  # x, y, w, h


def compute_crop(img_w, img_h, face_box):
    target_ratio = TARGET_W / TARGET_H

    if face_box is not None:
        fx, fy, fw, fh = face_box
        cx = fx + fw / 2
        cy = fy + fh / 2
        # crop height ~ 3.4x face height so hair + shoulders are included
        crop_h = fh * 3.4
        crop_w = crop_h * target_ratio
        # face center sits about 38% down from the top of the crop
        top = cy - crop_h * 0.42
        left = cx - crop_w / 2
    else:
        # fallback: center crop, trimmed 4% inward to drop scan borders
        crop_h = img_h * 0.92
        crop_w = crop_h * target_ratio
        if crop_w > img_w * 0.92:
            crop_w = img_w * 0.92
            crop_h = crop_w / target_ratio
        top = (img_h - crop_h) / 2
        left = (img_w - crop_w) / 2

    # clamp into image bounds, preserving crop size where possible
    if crop_w > img_w:
        crop_w = img_w
    if crop_h > img_h:
        crop_h = img_h
    left = max(0, min(left, img_w - crop_w))
    top = max(0, min(top, img_h - crop_h))

    return int(left), int(top), int(left + crop_w), int(top + crop_h)


def tune(path):
    cv_img = cv2.imread(path)
    if cv_img is None:
        print("skip (unreadable):", path)
        return
    h, w = cv_img.shape[:2]
    face_box = detect_face_box(cv_img)
    box = compute_crop(w, h, face_box)

    im = Image.open(path).convert("RGB")
    im = im.crop(box)
    im = im.resize((TARGET_W, TARGET_H), Image.LANCZOS)

    # normalize levels (fixes washed-out / low-contrast scans), then a
    # gentle contrast + saturation lift so every card reads consistently
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(1.08)
    im = ImageEnhance.Sharpness(im).enhance(1.15)

    im.save(path, "JPEG", quality=90)
    print("tuned:", os.path.basename(path), "face" if face_box is not None else "fallback-crop")


for fname in sorted(os.listdir(SRC_DIR)):
    if fname.lower().endswith(".jpg"):
        tune(os.path.join(SRC_DIR, fname))

print("done")
