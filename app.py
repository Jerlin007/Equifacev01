"""
===============================================================================
FastAPI Web Application for Facial Symmetry Analysis
-------------------------------------------------------------------------------
This application:
  - Accepts image uploads via POST /upload.
  - Preprocesses images (correct orientation, color mode, resizing).
  - Uses MediaPipe's Face Mesh to detect facial landmarks.
  - Computes facial symmetry scores.
  - Returns results as JSON (no images stored, all in-memory).
===============================================================================
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image, ImageOps, ExifTags
import cv2
import mediapipe as mp
import numpy as np

# -----------------------------------------------------------------------------
# FastAPI App Config
# -----------------------------------------------------------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# MediaPipe Face Mesh Initialization
# -----------------------------------------------------------------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

# -----------------------------------------------------------------------------
# Image Preprocessing Function
# -----------------------------------------------------------------------------
def preprocess_image(pil_img: Image.Image) -> Image.Image:
    try:
        exif = pil_img._getexif()
    except Exception:
        exif = None

    if exif is not None:
        orientation_tag = None
        for tag, value in ExifTags.TAGS.items():
            if value == "Orientation":
                orientation_tag = tag
                break
        if orientation_tag in exif and exif[orientation_tag] != 1:
            pil_img = ImageOps.exif_transpose(pil_img)

    if pil_img.mode == "RGBA":
        pil_img = pil_img.convert("RGB")

    pil_img = pil_img.resize((310, 413))
    return pil_img

# -----------------------------------------------------------------------------
# Facial Symmetry Analysis
# -----------------------------------------------------------------------------
def analyze_symmetry_mediapipe(pil_img: Image.Image) -> dict:
    pil_img = preprocess_image(pil_img)

    image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(image_rgb)
    if not results.multi_face_landmarks:
        return {"error": "No face detected"}

    landmarks = results.multi_face_landmarks[0].landmark
    image_height, image_width, _ = image.shape
    points = [
        (int(landmark.x * image_width), int(landmark.y * image_height))
        for landmark in landmarks
    ]

    eyes_symmetry = max(0, 100 - abs(points[33][0] - points[133][0]))
    mouth_symmetry = max(0, 100 - abs(points[62][0] - points[314][0]))
    nose_symmetry = max(0, 100 - abs(points[31][0] - points[35][0]))
    eyebrows_symmetry = max(0, 100 - abs(points[21][1] - points[22][1]))
    jawline_symmetry = max(0, 100 - abs(points[5][1] - points[11][1]))

    midline_x = (points[27][0] + points[30][0]) // 2
    vertical_symmetry_diff = 0
    count = 0
    for i, j in zip(range(17), range(16, -1, -1)):
        left_point = points[i]
        right_point = points[j]
        vertical_symmetry_diff += abs((2 * midline_x) - (left_point[0] + right_point[0]))
        count += 1
    vertical_symmetry = max(0, 100 - (vertical_symmetry_diff / count))

    eye_top = (points[37][1] + points[38][1] + points[43][1] + points[44][1]) / 4
    eye_bottom = (points[40][1] + points[41][1] + points[46][1] + points[47][1]) / 4
    horizontal_symmetry_diff = abs(eye_bottom - eye_top)
    horizontal_symmetry = max(0, 100 - horizontal_symmetry_diff)

    overall_symmetry = np.mean([
        eyes_symmetry, mouth_symmetry, nose_symmetry,
        eyebrows_symmetry, jawline_symmetry,
        vertical_symmetry, horizontal_symmetry,
    ])

    return {
        "eyes": eyes_symmetry,
        "mouth": mouth_symmetry,
        "nose": nose_symmetry,
        "eyebrows": eyebrows_symmetry,
        "jawline": jawline_symmetry,
        "vertical_symmetry": vertical_symmetry,
        "horizontal_symmetry": horizontal_symmetry,
        "overall": overall_symmetry,
    }

# -----------------------------------------------------------------------------
# FastAPI Routes
# -----------------------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "Face Symmetry FastAPI backend running 🎉"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg")):
        return JSONResponse(content={"error": "Invalid file type"}, status_code=400)

    try:
        contents = await file.read()
        pil_img = Image.open(BytesIO(contents))
        analysis_results = analyze_symmetry_mediapipe(pil_img)
    except Exception as e:
        return JSONResponse(content={"error": f"Error in analyzing image: {str(e)}"}, status_code=500)

    return JSONResponse(content=analysis_results)

# -----------------------------------------------------------------------------
# Entry point for local dev
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))  # Koyeb assigns a dynamic port
    app.run(host="0.0.0.0", port=port)






