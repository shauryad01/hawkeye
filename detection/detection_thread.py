import time
from PySide6.QtCore import QThread, Signal
from detection.pose_detector import PoseDetector
from risk_engine.risk_engine import RiskEngine

from tracking.tracker import CentroidTracker


class DetectionThread(QThread):
    result_ready = Signal(object, object, float)

    def __init__(self):
        super().__init__()
        self.risk_engine = RiskEngine()
        self.detector = PoseDetector()
        self.latest_frame = None
        self.running = False
        self.tracker = CentroidTracker()


    def submit_frame(self, frame):
        self.latest_frame = frame

    def run(self):
        self.running = True

        while self.running:
            if self.latest_frame is None:
                time.sleep(0.01)
                continue

            frame = self.latest_frame
            self.latest_frame = None  # DROP old frames

            detections = self.detector.detect(frame)
            detections = self.tracker.update(detections)
            self.result_ready.emit(frame, detections)
            detections = self.detector.detect(frame)
            detections = self.tracker.update(detections)

            risk = self.risk_engine.update(detections)
            self.result_ready.emit(frame, detections, risk)
            


            time.sleep(0.01)

    def stop(self):
        self.running = False
        self.wait()
