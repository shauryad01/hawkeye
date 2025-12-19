import sys
from PySide6.QtWidgets import QApplication
from detection.detection_thread import DetectionThread
from settings import CAMERA_SRC
from ui.main_window import MainWindow
from camera.camera_thread import CameraThread


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    camera_thread = CameraThread(src=CAMERA_SRC)
    detection_thread = DetectionThread()

    camera_thread.frame_ready.connect(detection_thread.submit_frame)
    detection_thread.result_ready.connect(window.update_frame)

    camera_thread.start()
    detection_thread.start()


    def cleanup():
        camera_thread.stop()
        detection_thread.stop()


    app.aboutToQuit.connect(cleanup)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
