import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from camera.camera_thread import CameraThread


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    camera_thread = CameraThread(src=0)
    camera_thread.frame_ready.connect(window.update_frame)
    camera_thread.start()

    def cleanup():
        camera_thread.stop()

    app.aboutToQuit.connect(cleanup)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
