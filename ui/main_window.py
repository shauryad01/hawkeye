from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
import cv2
import settings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HawkEye")
        self.resize(900, 600)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)


        self.video_label.setFixedSize(800, 450)

        self.setCentralWidget(self.video_label)

    def update_frame(self, frame, detections=None, risk=0.0):

        """
        Receives a BGR frame
        """
        if detections is not None:
            self.draw_detections(frame, detections)

        h, w, ch = frame.shape
        bytes_per_line = ch * w

        qimg = QImage(
            frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_BGR888
        )

        pixmap = QPixmap.fromImage(qimg)

        # aspect ratio 
        pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.video_label.setPixmap(pixmap)
        cv2.putText(
            frame,
            f"RISK: {int(risk * 100)}%",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255) if risk > 0.7 else (0, 255, 255),
            3
        )


    def draw_detections(self, frame, detections):
        for d in detections:
            x1, y1, x2, y2 = map(int, d["bbox"])

            if settings.DEBUG:
                # Draw bounding box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )
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


                # Draw keypoints
                keypoints = d["keypoints"]
                for x, y, conf in keypoints:
                    if conf > 0.5:
                        cv2.circle(
                            frame,
                            (int(x), int(y)),
                            3,
                            (0, 0, 255),
                            -1
                        )

