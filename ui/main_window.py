from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HawkEye")
        self.resize(900, 600)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)


        self.video_label.setFixedSize(800, 450)

        self.setCentralWidget(self.video_label)

    def update_frame(self, frame):
        """
        Receives a BGR frame
        """
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
