from ultralytics import YOLO
import uuid

# Load the YOLO model
model = YOLO("../weights/best.pt")  # Adjust this path if necessary

def detect_objects(image):
    results = model.predict(image, conf=0.5)
    detections = []

    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = box.conf[0].item()
                class_id = int(box.cls[0].item())


                label = "stamp"  # 🔥 hardcoded label for single-class detection


                width = x2 - x1
                height = y2 - y1
                detections.append({
    "x": x1 + width / 2,
    "y": y1 + height / 2,
    "width": width,
    "height": height,
    "confidence": confidence,
    "class": label,           # ✅ use name not ID
    "class_id": class_id,
    "detection_id": str(uuid.uuid4())
})

    return detections
