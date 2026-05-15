import io
import json
import logging
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ultralytics import YOLO

# ---------------------------------------------------------------------------
# Config — paths to my trained weights
# ---------------------------------------------------------------------------
DETECTION_MODEL_PATH = "/home/donia/smart_agriculture_project/detection_best.pt"
SEGMENTATION_MODEL_PATH = "/home/donia/smart_agriculture_project/segmentation_best.pt"
CONFIDENCE_THRESHOLD = 0.25


logger = logging.getLogger("yolo-api")

# ---------------------------------------------------------------------------
# Models are loaded once at startup and reused across requests
# ---------------------------------------------------------------------------
models: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading YOLO models...")
    models["detect"] = YOLO(DETECTION_MODEL_PATH)
    '''models["detect"].model.names = {
        0: "Bacterial Blight",
        1: "Curl Virus",
        2: "Healthy",               
        3: "Septoria Leaf Spot",    
        4: "Yellow Leaf Curl",      
        5: "Herbicide Injury",      
        6: "Leaf Crinkle",          
        7: "Leaf Curl",             
        8: "Leaf Spot",             
        9: "Mosaic Virus",          
        10: "Powdery Mildew",       
        11: "Sudden Death",         
        12: "Target Spot"           
    }'''

    models["detect"].model.names = {
        0: "Affected",
        1: "Affected",
        2: "Healthy",
        3: "Affected",
        4: "Affected",
        5: "Affected",
        6: "Affected",
        7: "Affected",
        8: "Affected",
        9: "Affected",
        10: "Affected",
        11: "Affected",
        12: "Affected"
    }

    models["segment"] = YOLO(SEGMENTATION_MODEL_PATH)
    """models["segment"].model.names = {
        0: "Bacterial Blight",
        1: "Curl Virus",
        2: "Herbicide Injury",
        3: "Leaf Crinkle",
        4: "Leaf Curl",
        5: "Leaf Spot",
        6: "Mosaic Virus",
        7: "Powdery Mildew",
        8: "Sudden Death",
        9: "Target Spot",
        10: "Healthy",
        11: "Septoria Leaf Spot",
        12: "Yellow Leaf Curl",
    }"""
    logger.info("Models loaded successfully.")
    yield
    models.clear()


app = FastAPI(
    title="YOLO Inference API",
    description="YOLOv11 object detection and segmentation endpoints.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Pydantic response schemas
# ---------------------------------------------------------------------------
class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    label: str
    confidence: float
    bbox: BoundingBox


class SegmentationResult(BaseModel):
    label: str
    confidence: float
    bbox: BoundingBox
    mask_polygon: list[list[float]] | None  # [[x,y], ...] contour points


class DetectionResponse(BaseModel):
    detections: list[Detection]


class SegmentationResponse(BaseModel):
    results: list[SegmentationResult]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def decode_image(file_bytes: bytes) -> np.ndarray:
    """Decode uploaded bytes to an OpenCV BGR image."""
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Make sure it is a valid JPEG/PNG.")
    return img


def image_to_streaming_response(img: np.ndarray, predictions: list | dict) -> StreamingResponse:
    """Encode annotated image as JPEG and stream it back with predictions in a header."""
    success, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode annotated image.")
    return StreamingResponse(
        io.BytesIO(buffer.tobytes()),
        media_type="image/jpeg",
        headers={"X-Predictions": json.dumps(predictions)},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post(
    "/detect",
    summary="Object Detection",
    description="Upload an image and get back the annotated JPEG. Predictions (labels, confidences, bboxes) are in the X-Predictions response header as JSON.",
    response_class=StreamingResponse,
)
async def detect(file: UploadFile = File(..., description="Image file (JPEG or PNG)")):
    raw = await file.read()
    img = decode_image(raw)

    results = models["detect"].predict(source=img, conf=CONFIDENCE_THRESHOLD, verbose=False)
    result = results[0]

    detections = []
    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        label = result.names[int(box.cls[0])]
        detections.append({
            "label": label,
            "confidence": round(conf, 4),
            "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        })

    annotated = result.plot(labels=True, conf=True, line_width=2, font_size=12)
    return image_to_streaming_response(annotated, detections)


@app.post(
    "/segment",
    summary="Instance Segmentation",
    description="Upload an image and get back the annotated JPEG. Predictions (labels, confidences, bboxes, mask polygons) are in the X-Predictions response header as JSON.",
    response_class=StreamingResponse,
)
async def segment(file: UploadFile = File(..., description="Image file (JPEG or PNG)")):
    raw = await file.read()
    img = decode_image(raw)

    results = models["segment"].predict(source=img, conf=CONFIDENCE_THRESHOLD, verbose=False)
    result = results[0]

    seg_results = []
    masks = result.masks

    for i, box in enumerate(result.boxes):
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        label = result.names[int(box.cls[0])]

        polygon = None
        if masks is not None and i < len(masks.xy):
            polygon = masks.xy[i].tolist()

        seg_results.append({
            "label": label,
            "confidence": round(conf, 4),
            "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "mask_polygon": polygon,
        })

    annotated = result.plot()
    return image_to_streaming_response(annotated, seg_results)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", summary="Health Check")
async def health():
    return {"status": "ok", "models_loaded": list(models.keys())}