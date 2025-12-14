import cv2
import time
from PySide6.QtCore import QThread, Signal


class CameraThread(QThread):
    frame_ready = Signal(object)

    def __init__(self, src=0):
        super().__init__()
        self.src = src
        self.running = False

    def run(self):
        cap = cv2.VideoCapture(self.src)

        if not cap.isOpened():
            print("Failed to open camera")
            return

        self.running = True

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            self.frame_ready.emit(frame)

            time.sleep(0.01)

        cap.release()

    def stop(self):
        self.running = False
        self.wait()
