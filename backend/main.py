from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO

from backend.model import detect_objects

import cv2
import threading

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global detection buffer
latest_detections = []

# Global camera control
camera = None
camera_lock = threading.Lock()

@app.get("/")
def home():
    return {"message": "Stamp Detection API is running 🎯"}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    image_data = await file.read()
    image = Image.open(BytesIO(image_data)).convert("RGB")
    results = detect_objects(image)

    global latest_detections
    latest_detections = results

    return {"detections": results}

@app.get("/detect/latest")
def get_latest():
    return {"detections": latest_detections}

def generate_video_stream():
    global camera

    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(0)

    while True:
        with camera_lock:
            if camera is None:
                break
            ret, frame = camera.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detect_objects(Image.fromarray(rgb))

        for det in results:
            x, y, w, h = int(det['x']), int(det['y']), int(det['width']), int(det['height'])
            label = f"{det['class']} {det['confidence']:.2f}"
            top_left = (x - w//2, y - h//2)
            bottom_right = (x + w//2, y + h//2)
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(frame, label, (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        _, jpeg = cv2.imencode('.jpg', frame)
        if not _:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stop_video")
def stop_video():
    global camera
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
    return {"status": "Camera stopped"}


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
