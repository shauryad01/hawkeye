from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap
import cv2
import settings
from ui.alert_dialog import AlertDialog
import time


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HawkEye")
        self.resize(900, 600)

        self.video_label = QLabel("Waiting for video…", self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(800, 450)
        self.video_label.setStyleSheet("background-color: black; color: white;")

        self.setCentralWidget(self.video_label)

        # Alert system
        self.alert_dialog = AlertDialog(self)
        self.last_alert_time = 0
        self.ALERT_THRESHOLD = 0.75
        self.ALERT_COOLDOWN = 5  # seconds

    def handle_risk(self, risk):
        now = time.time()
        if risk >= self.ALERT_THRESHOLD:
            if now - self.last_alert_time > self.ALERT_COOLDOWN:
                self.last_alert_time = now
                self.alert_dialog.show()


    @Slot(object, object, float)
    def on_frame_received(self, frame, detections, risk):
        # defensive copy
        frame = frame.copy()

        if detections:
            self.draw_detections(frame, detections)

        # draw risk BEFORE rendering
        cv2.putText(
            frame,
            f"RISK: {int(risk * 100)}%",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255) if risk > 0.7 else (0, 255, 255),
            3,
            cv2.LINE_AA
        )

        self.render_frame(frame)
        self.handle_risk(risk)

    def render_frame(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w

        qimg = QImage(
            frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_BGR888
        )

        pixmap = QPixmap.fromImage(qimg).scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.video_label.setPixmap(pixmap)


    def draw_detections(self, frame, detections):
        if not settings.DEBUG:
            return

        for d in detections:
            x1, y1, x2, y2 = map(int, d["bbox"])

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            pid = d.get("id", -1)
            cv2.putText(
                frame,
                f"ID {pid}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                2
            )

            for x, y, conf in d["keypoints"]:
                if conf > 0.5:
                    cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), -1)
