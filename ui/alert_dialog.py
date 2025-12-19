from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer


class AlertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)


        self.setWindowTitle("ALERT")
        self.setModal(True)
        self.setFixedSize(400, 200)

        label = QLabel("POTENTIAL UNSAFE INTERACTION DETECTED")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(label)

        # RED WARNING
        self.setStyleSheet("""
            QDialog {
                background-color: #8B0000;
            }
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        QTimer.singleShot(3000, self.close)
