import numpy as np
from ultralytics import YOLO


class PoseDetector:
    def __init__(self, model_path="yolov8n-pose.pt", conf=0.3):
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, frame):
        results = self.model(frame, conf=self.conf, verbose=False)
        detections = []

        for r in results:
            if r.keypoints is None:
                continue

            boxes = r.boxes
            keypoints = r.keypoints

            for i in range(len(boxes)):
                x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                score = float(boxes.conf[i].cpu().numpy())

                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                kpts = keypoints.xy[i].cpu().numpy()
                kpts_conf = keypoints.conf[i].cpu().numpy()

                kpts_full = np.hstack([
                    kpts,
                    kpts_conf.reshape(-1, 1)
                ])

                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "center": (cx, cy),
                    "keypoints": kpts_full,
                    "score": score
                })

        return detections
